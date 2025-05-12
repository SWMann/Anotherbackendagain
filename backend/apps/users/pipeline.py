def get_discord_avatar(backend, user, response, *args, **kwargs): 
    """Add discord avatar URL to user.""" 
    if backend.name == 'discord': 
        if response.get('avatar'): 
            user.avatar_url = f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}.png" 
            user.save() 
