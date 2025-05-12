class ProfileSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = User 
        fields = [ 
            'id', 'username', 'avatar_url', 'bio', 'service_number', 
            'current_rank', 'primary_unit', 'branch', 'background_image_url', 
            'timezone', 'commission_stage', 'recruit_status', 
            'officer_candidate', 'warrant_officer_candidate' 
        ] 
        read_only_fields = ['id', 'service_number', 'current_rank', 'primary_unit', 'branch', 'commission_stage', 'recruit_status'] 
 
class DiscordTokenObtainPairSerializer(TokenObtainPairSerializer): 
    @classmethod 
    def get_token(cls, user): 
        token = super().get_token(user) 
ECHO is off.
        # Add custom claims 
        token['discord_id'] = user.discord_id 
        token['username'] = user.username 
        token['is_admin'] = user.is_admin 
        token['is_staff'] = user.is_staff 
ECHO is off.
        return token 
 
class UserProfileSerializer(serializers.ModelSerializer): 
    rank = serializers.SerializerMethodField() 
    unit = serializers.SerializerMethodField() 
    branch = serializers.SerializerMethodField() 
ECHO is off.
    class Meta: 
        model = User 
        fields = [ 
            'id', 'username', 'avatar_url', 'bio', 'join_date', 
            'service_number', 'rank', 'unit', 'branch', 
            'background_image_url', 'commission_stage', 'recruit_status', 
        ] 
ECHO is off.
    def get_rank(self, obj): 
        if obj.current_rank: 
            return { 
                'id': obj.current_rank.id, 
                'name': obj.current_rank.name, 
                'abbreviation': obj.current_rank.abbreviation, 
                'insignia_image_url': obj.current_rank.insignia_image_url 
            } 
        return None 
ECHO is off.
    def get_unit(self, obj): 
        if obj.primary_unit: 
            return { 
                'id': obj.primary_unit.id, 
                'name': obj.primary_unit.name, 
                'abbreviation': obj.primary_unit.abbreviation, 
                'emblem_url': obj.primary_unit.emblem_url 
            } 
        return None 
ECHO is off.
    def get_branch(self, obj): 
        if obj.branch: 
            return { 
                'id': obj.branch.id, 
                'name': obj.branch.name, 
                'abbreviation': obj.branch.abbreviation, 
                'logo_url': obj.branch.logo_url 
            } 
        return None 
