import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_settings.dart';

class PhraseCheck {
  final String baseUrl = ApiSettings.baseUrl;

  Future<Map<String, dynamic>> createPhrase({required String text}) async {
    final url = Uri.parse(ApiSettings.generateEndpoint);
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode({'text': text}),
    );

    if (response.statusCode == 200) {
      final decoded = utf8.decode(response.bodyBytes);
      final data = jsonDecode(decoded);

      return {
        'minus_words': data['minus_words'] ?? [],
        'advice': data['advice'] ?? '結果なし',
      };
    } else {
      throw Exception('通信エラー: ${response.statusCode}');
    }
  }
}
