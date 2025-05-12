#/bin/bash 
 
# Apply database migrations 
echo "Applying database migrations..." 
python manage.py migrate 
 
# Create superuser if not exists 
echo "Creating superuser..." 
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(discord_id='admin').exists() or User.objects.create_superuser('admin', 'admin', 'admin@example.com', 'admin')" 
 
# Start server 
echo "Starting server..." 
exec "$@" 
