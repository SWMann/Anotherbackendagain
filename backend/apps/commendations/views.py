# backend/apps/commendations/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import CommendationType, Commendation, CommendationDevice
from .serializers import (
    CommendationTypeSerializer, CommendationSerializer,
    AwardCommendationSerializer, CreateCommendationTypeSerializer,
    CommendationDeviceSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model
from apps.core.views import MediaContextMixin

User = get_user_model()


class CommendationTypeViewSet(MediaContextMixin, viewsets.ModelViewSet):
    """ViewSet for commendation types management"""
    queryset = CommendationType.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'requires_nomination', 'multiple_awards_allowed']
    search_fields = ['name', 'abbreviation', 'description', 'eligibility_criteria']
    ordering_fields = ['precedence', 'name', 'category']
    ordering = ['precedence']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateCommendationTypeSerializer
        return CommendationTypeSerializer

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get commendation types grouped by category"""
        categories = {}
        for comm_type in self.queryset.filter(is_active=True):
            category = comm_type.category
            if category not in categories:
                categories[category] = []
            categories[category].append(CommendationTypeSerializer(comm_type, context={'request': request}).data)

        return Response(categories)

    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        """Get all recipients of this commendation type"""
        comm_type = self.get_object()
        commendations = Commendation.objects.filter(
            commendation_type=comm_type
        ).select_related('user', 'user__current_rank', 'awarded_by')

        # Apply filters
        is_public = request.query_params.get('is_public')
        if is_public is not None:
            commendations = commendations.filter(is_public=is_public.lower() == 'true')

        is_verified = request.query_params.get('is_verified')
        if is_verified is not None:
            commendations = commendations.filter(is_verified=is_verified.lower() == 'true')

        serializer = CommendationSerializer(commendations, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this commendation type"""
        comm_type = self.get_object()

        total_awarded = Commendation.objects.filter(commendation_type=comm_type).count()
        unique_recipients = Commendation.objects.filter(
            commendation_type=comm_type
        ).values('user').distinct().count()

        # Awards by month for the last year
        from datetime import datetime, timedelta
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)

        monthly_awards = []
        current = start_date
        while current < end_date:
            month_end = current.replace(day=28) + timedelta(days=4)
            month_end = month_end - timedelta(days=month_end.day)

            count = Commendation.objects.filter(
                commendation_type=comm_type,
                awarded_date__gte=current,
                awarded_date__lte=month_end
            ).count()

            monthly_awards.append({
                'month': current.strftime('%Y-%m'),
                'count': count
            })

            current = month_end + timedelta(days=1)

        return Response({
            'total_awarded': total_awarded,
            'unique_recipients': unique_recipients,
            'monthly_awards': monthly_awards,
            'multiple_award_recipients': Commendation.objects.filter(
                commendation_type=comm_type
            ).values('user').annotate(
                count=Count('id')
            ).filter(count__gt=1).count()
        })


class CommendationViewSet(MediaContextMixin, viewsets.ModelViewSet):
    """ViewSet for individual commendations"""
    queryset = Commendation.objects.all()
    serializer_class = CommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'commendation_type', 'is_public', 'is_verified', 'related_unit']
    search_fields = ['citation', 'short_citation', 'order_number']
    ordering_fields = ['awarded_date', 'commendation_type__precedence']
    ordering = ['-awarded_date']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-admin users can only see public commendations
        if not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(is_public=True) | Q(user=self.request.user)
            )

        return queryset.select_related(
            'user', 'user__current_rank', 'commendation_type',
            'awarded_by', 'verified_by', 'related_event', 'related_unit'
        ).prefetch_related('devices', 'devices__device')

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently awarded commendations"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timezone.timedelta(days=days)

        recent_commendations = self.get_queryset().filter(
            awarded_date__gte=since_date,
            is_public=True
        )

        page = self.paginate_queryset(recent_commendations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_commendations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def award(self, request):
        """Award a commendation to a user"""
        serializer = AwardCommendationSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            # Get the next award number for this user/commendation combination
            existing_awards = Commendation.objects.filter(
                user_id=data['user_id'],
                commendation_type_id=data['commendation_type_id']
            ).aggregate(max_award=Count('id'))

            award_number = (existing_awards['max_award'] or 0) + 1

            # Create the commendation
            commendation = Commendation.objects.create(
                user_id=data['user_id'],
                commendation_type_id=data['commendation_type_id'],
                awarded_date=data['awarded_date'],
                awarded_by=request.user,
                citation=data['citation'],
                short_citation=data['short_citation'],
                related_event_id=data.get('related_event_id'),
                related_unit_id=data.get('related_unit_id'),
                order_number=data.get('order_number'),
                is_public=data.get('is_public', True),
                supporting_documents=data.get('supporting_documents', []),
                award_number=award_number
            )

            # Add any devices
            for device_data in data.get('devices', []):
                if 'device_id' in device_data:
                    commendation.devices.create(
                        device_id=device_data['device_id'],
                        quantity=device_data.get('quantity', 1)
                    )

            return Response(
                CommendationSerializer(commendation, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None):
        """Verify a commendation"""
        commendation = self.get_object()

        if commendation.is_verified:
            return Response(
                {'detail': 'Commendation is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        commendation.is_verified = True
        commendation.verified_by = request.user
        commendation.verified_date = timezone.now()
        commendation.save()

        return Response(CommendationSerializer(commendation, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def user_commendations(self, request):
        """Get commendations for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)

        # Check permissions
        if not request.user.is_admin and request.user.id != user.id:
            # Only show public commendations for other users
            commendations = self.get_queryset().filter(user=user, is_public=True)
        else:
            commendations = self.get_queryset().filter(user=user)

        # Group by commendation type for ribbon rack display
        grouped = {}
        for comm in commendations:
            type_id = str(comm.commendation_type.id)
            if type_id not in grouped:
                grouped[type_id] = {
                    'commendation_type': CommendationTypeSerializer(
                        comm.commendation_type,
                        context={'request': request}
                    ).data,
                    'awards': []
                }
            grouped[type_id]['awards'].append(
                CommendationSerializer(comm, context={'request': request}).data
            )

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'rank': user.current_rank.abbreviation if user.current_rank else None
            },
            'commendations': list(grouped.values()),
            'total_commendations': commendations.count(),
            'unique_commendations': len(grouped)
        })


class CommendationDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for commendation devices"""
    queryset = CommendationDevice.objects.all()
    serializer_class = CommendationDeviceSerializer
    permission_classes = [IsAdminOrReadOnly]