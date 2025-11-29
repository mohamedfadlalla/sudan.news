# Push Notification Implementation Documentation

## Overview

This document provides a comprehensive overview of the push notification system implemented in the Sudan News Aggregator backend. The system uses Firebase Cloud Messaging (FCM) to deliver push notifications to Android (and potentially iOS) devices.

## Architecture

### Components

1. **NotificationService** (`sudan-news-api/src/notification_service.py`)
   - Core service handling FCM integration
   - Manages Firebase Admin SDK initialization
   - Provides methods for different notification types

2. **TokenRepository** (`shared_models/repositories/token_repository.py`)
   - Manages device registration tokens
   - Stores user-device relationships
   - Handles token lifecycle (creation, updates, cleanup)

3. **API Endpoints** (`sudan-news-api/src/app.py`)
   - RESTful endpoints for notification management
   - Token registration and notification sending

4. **Database Models** (`shared_models/models.py`)
   - `UserToken` table for storing FCM tokens
   - User and device relationship management

## Database Schema

### UserToken Table

```sql
CREATE TABLE user_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    device_id VARCHAR,
    token VARCHAR NOT NULL,
    platform VARCHAR, -- 'android' or 'ios'
    created_at VARCHAR,
    updated_at VARCHAR,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Fields:**
- `id`: Primary key
- `user_id`: Optional user association
- `device_id`: Unique device identifier
- `token`: FCM registration token
- `platform`: Device platform ('android'/'ios')
- `created_at`: Token creation timestamp
- `updated_at`: Last token update timestamp

## Firebase Configuration

### Environment Variables

```bash
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=C:\Users\DELL\Desktop\GN\Sudan-new-Backend\firebase_key.json

# Notification Settings
NOTIFICATION_SOURCE_THRESHOLD=10
```

### Firebase Credentials

The system requires a Firebase service account key JSON file. The path is configured via `FIREBASE_CREDENTIALS_PATH` environment variable.

**Default paths:**
- Windows: `C:\Users\DELL\Desktop\GN\Sudan-new-Backend\firebase_key.json`
- Linux/Production: `/var/www/sudanese_news/shared/firebase_key.json`

## Notification Types

### 1. Custom Notifications

Send custom notifications to all registered users.

**API Endpoint:** `POST /api/send_notification`

**Request Body:**
```json
{
  "title": "Breaking News",
  "body": "Important announcement",
  "data": {
    "customKey": "customValue"
  }
}
```

### 2. New Cluster Notifications

Automatically generated notifications when new news clusters are created.

**Trigger:** Manual API call or external system integration

**Content:**
- Title: "خبر جديد" (New News)
- Body: "تم نشر مجموعة أخبار جديدة: [cluster title]" (New news cluster published)

**Data Payload:**
```json
{
  "clusterId": "123",
  "type": "new_cluster"
}
```

### 3. Popular Cluster Notifications

Notifications for clusters covered by many sources (above threshold).

**Trigger:** Manual API call or automated system

**Threshold:** Configurable via `NOTIFICATION_SOURCE_THRESHOLD` (default: 10)

**Content:**
- Title: "أهم الأخبار" (Most Important News)
- Body: "مجموعة أخبار تغطيها [count] مصدر: [cluster title]" (News cluster covered by X sources)

**Data Payload:**
```json
{
  "clusterId": "123",
  "type": "popular_cluster",
  "sourceCount": "15"
}
```

## API Endpoints

### Token Management

#### Register Device Token
`POST /api/register_token`

**Request Body:**
```json
{
  "user_id": 123,
  "device_id": "device-uuid",
  "token": "fcm-registration-token",
  "platform": "android"
}
```

**Response:**
```json
{
  "success": true
}
```

### Notification Sending

#### Send Custom Notification
`POST /api/send_notification`

**Request Body:**
```json
{
  "title": "Notification Title",
  "body": "Notification body text",
  "data": {
    "key": "value"
  }
}
```

**Response:**
```json
{
  "success": 150,
  "failure": 2
}
```

#### Send New Cluster Notification
`POST /api/notify_new_cluster/<cluster_id>`

**Response:**
```json
{
  "success": 150,
  "failure": 2
}
```

#### Send Popular Clusters Notifications
`POST /api/notify_popular_clusters`

**Response:**
```json
{
  "total_clusters": 3,
  "results": [
    {
      "cluster_id": 123,
      "title": "Breaking News Title",
      "sources": 12,
      "notification_result": {
        "success": 150,
        "failure": 2
      }
    }
  ]
}
```

### Statistics and Monitoring

#### Get Notification Statistics
`GET /api/notification_stats`

**Response:**
```json
{
  "token_stats": {
    "total_tokens": 152,
    "platform_distribution": {
      "android": 145,
      "ios": 7
    }
  },
  "popular_clusters_count": 3,
  "popular_clusters": [
    {
      "id": 123,
      "title": "Cluster Title",
      "number_of_sources": 12
    }
  ],
  "firebase_initialized": true
}
```

## Android Integration

### Notification Icons

The system provides notification icons in multiple densities:

- `ic_notification_hdpi.png` (72x72px)
- `ic_notification_mdpi.png` (48x48px)
- `ic_notification_xhdpi.png` (96x96px)
- `ic_notification_xxhdpi.png` (144x144px)
- `ic_notification_xxxhdpi.png` (192x192px)

**Location:** `sudan-news-api/static/img/`

### FCM Message Structure

```json
{
  "message": {
    "notification": {
      "title": "خبر جديد",
      "body": "تم نشر مجموعة أخبار جديدة"
    },
    "data": {
      "clusterId": "123",
      "type": "new_cluster"
    },
    "token": "device-fcm-token"
  }
}
```

### Android Manifest Configuration

```xml
<!-- FCM Permissions -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="com.google.android.c2dm.permission.RECEIVE" />

<!-- FCM Service -->
<service
    android:name=".MyFirebaseMessagingService"
    android:exported="false">
    <intent-filter>
        <action android:name="com.google.firebase.MESSAGING_EVENT" />
    </intent-filter>
</service>
```

## Token Management

### Token Lifecycle

1. **Registration:** Device registers FCM token with backend
2. **Storage:** Token stored with device ID and user association
3. **Updates:** Token refreshed when FCM provides new token
4. **Cleanup:** Expired tokens removed periodically

### Token Repository Methods

- `store_or_update_token()`: Register or update device token
- `get_token_by_value()`: Retrieve token information
- `get_tokens_by_user()`: Get all tokens for a user
- `get_all_active_tokens()`: Get all tokens for notifications
- `delete_token()`: Remove specific token
- `cleanup_expired_tokens()`: Remove old tokens

## Error Handling

### FCM Errors

The system handles common FCM errors:
- Invalid/expired tokens
- Network failures
- Quota exceeded
- Authentication errors

### Token Cleanup

- Automatic removal of invalid tokens during sending
- Periodic cleanup of expired tokens (90 days default)
- Manual token management via API

## Security Considerations

### Token Storage
- Tokens stored securely in database
- No sensitive information in notification payloads
- HTTPS required for all API communications

### Firebase Security
- Service account credentials properly secured
- Environment-specific credential paths
- Minimal required permissions for FCM

## Monitoring and Analytics

### Metrics Tracked
- Total registered tokens
- Platform distribution (Android/iOS)
- Notification success/failure rates
- Popular clusters count

### Logging
- FCM initialization status
- Notification sending results
- Token registration events
- Error conditions

## Deployment Considerations

### Environment Setup
1. Configure Firebase project
2. Download service account key
3. Set environment variables
4. Deploy notification icons

### Production Configuration
- Use production Firebase project
- Configure proper credential paths
- Set up monitoring and alerting
- Implement token cleanup schedules

## Integration Points

### With News Pipeline
- Notifications triggered after cluster creation
- Popular cluster detection based on source count
- Automated notification scheduling (future enhancement)

### With Mobile App
- Token registration on app startup
- Notification handling and display
- Deep linking to specific content

## Future Enhancements

### Automated Notifications
- Schedule notifications for trending topics
- Time-based notification delivery
- User preference-based filtering

### Advanced Features
- Rich notifications with images
- Notification categories and channels
- User segmentation and targeting

### Analytics
- Notification open rates
- User engagement metrics
- A/B testing capabilities

## Troubleshooting

### Common Issues

1. **Firebase not initialized**
   - Check credential file path
   - Verify JSON format
   - Check file permissions

2. **No notifications received**
   - Verify FCM token registration
   - Check notification payload format
   - Review FCM console for delivery status

3. **Token errors**
   - Implement token refresh handling
   - Clean up expired tokens
   - Handle device unregistration

### Debug Endpoints
- `/api/notification_stats` for system status
- FCM console for delivery monitoring
- Application logs for error details

## Code Examples

### Register Token (Android/Kotlin)
```kotlin
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (!task.isSuccessful) {
        Log.w(TAG, "Fetching FCM registration token failed", task.exception)
        return@addOnCompleteListener
    }

    val token = task.result
    registerTokenWithBackend(token)
}
```

### Handle Notification (Android/Kotlin)
```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        remoteMessage.notification?.let {
            showNotification(it.title, it.body, remoteMessage.data)
        }
    }

    override fun onNewToken(token: String) {
        registerTokenWithBackend(token)
    }
}
```

This documentation provides a complete reference for implementing and maintaining the push notification system in the Sudan News Aggregator application.
