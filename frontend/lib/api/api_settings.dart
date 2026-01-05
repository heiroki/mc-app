// lib/api/api_settings.dart（修正版）

class ApiSettings {
  // デスクトップアプリではローカルホスト固定
  static const String baseUrl = 'http://127.0.0.1:8000';
  
  // タイムアウト設定
  static const Duration timeout = Duration(seconds: 60);
  
  // エンドポイント
  static String get healthUrl => '$baseUrl/health';
  static String get generateEndpoint => '$baseUrl/generate';
  static String get conversationsEndpoint => '$baseUrl/conversations';
  static String get wordcloudEndpoint => '$baseUrl/wordcloud/generate';
}