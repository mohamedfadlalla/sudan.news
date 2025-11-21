from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models import UserToken, User

class TokenRepository:
    def __init__(self, session: Session):
        self.session = session

    def store_or_update_token(self, user_id: int = None, device_id: str = None,
                             token: str = None, platform: str = None) -> UserToken:
        """Store new token or update existing one"""
        if not all([device_id, token, platform]):
            raise ValueError("device_id, token, and platform are required")

        # Check if token already exists
        existing_token = self.session.query(UserToken).filter(UserToken.token == token).first()

        now = datetime.now().isoformat()

        if existing_token:
            # Update existing token
            existing_token.user_id = user_id
            existing_token.device_id = device_id
            existing_token.platform = platform
            existing_token.updated_at = now
            return existing_token
        else:
            # Create new token
            user_token = UserToken(
                user_id=user_id,
                device_id=device_id,
                token=token,
                platform=platform,
                created_at=now
            )
            self.session.add(user_token)
            self.session.flush()
            return user_token

    def get_token_by_value(self, token: str) -> Optional[UserToken]:
        """Get token by FCM token value"""
        return self.session.query(UserToken).filter(UserToken.token == token).first()

    def get_tokens_by_user(self, user_id: int) -> List[UserToken]:
        """Get all tokens for a user"""
        return self.session.query(UserToken).filter(UserToken.user_id == user_id).all()

    def get_all_active_tokens(self) -> List[Dict[str, str]]:
        """Get all active tokens for push notifications"""
        tokens = self.session.query(UserToken).filter(
            UserToken.token.isnot(None)
        ).all()

        return [{'token': t.token, 'platform': t.platform} for t in tokens]

    def delete_token(self, token: str) -> bool:
        """Delete a token"""
        user_token = self.get_token_by_value(token)
        if user_token:
            self.session.delete(user_token)
            self.session.commit()
            return True
        return False

    def cleanup_expired_tokens(self, days_old: int = 90) -> int:
        """Remove tokens that haven't been updated in specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_str = cutoff_date.isoformat()

        deleted_count = self.session.query(UserToken).filter(
            UserToken.updated_at < cutoff_str
        ).delete()

        self.session.commit()
        return deleted_count

    def get_token_stats(self) -> Dict[str, Any]:
        """Get statistics about stored tokens"""
        from sqlalchemy import func

        total_tokens = self.session.query(func.count(UserToken.id)).scalar()

        platform_counts = self.session.query(
            UserToken.platform, func.count(UserToken.id)
        ).group_by(UserToken.platform).all()

        return {
            'total_tokens': total_tokens,
            'platform_distribution': dict(platform_counts)
        }
