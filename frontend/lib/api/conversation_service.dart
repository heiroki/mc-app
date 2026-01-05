import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/conversation.dart';
import 'api_settings.dart';

class ConversationService {
  final String baseUrl = ApiSettings.baseUrl;

  // 会話履歴を取得
  Future<List<Conversation>> getConversations({
    int skip = 0,
    int limit = 100,
  }) async {

    var url = Uri.parse(
      '${ApiSettings.conversationsEndpoint}?skip=$skip&limit=$limit',
    );

    final response = await http.get(
      url,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
    );

    if (response.statusCode == 200) {
      final decoded = utf8.decode(response.bodyBytes);
      final List<dynamic> data = jsonDecode(decoded);
      return data.map((json) => Conversation.fromJson(json)).toList();
    } else {
      throw Exception('履歴の取得に失敗しました: ${response.statusCode}');
    }
  }

  // ← 修正: パラメータを変更（minus_words と advice を分離）
  Future<Conversation> saveConversation({
    required String userInput,
    required List<String> minusWords, // ← 追加
    required String advice, // ← 追加
  }) async {
    final url = Uri.parse(ApiSettings.conversationsEndpoint);
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      // ← 変更: データ構造を変更
      body: jsonEncode({
        'user_id': null, 
        'user_input': userInput,
        'ai_response_words': minusWords,
        'ai_response_advice': advice,
      }),
    );

    if (response.statusCode == 200) {
      final decoded = utf8.decode(response.bodyBytes);
      final data = jsonDecode(decoded);
      return Conversation.fromJson(data);
    } else {
      throw Exception('会話の保存に失敗しました: ${response.statusCode}');
    }
  }
}
