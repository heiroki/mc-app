import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'api_settings.dart';

class WordCloudService {
  final String baseUrl = ApiSettings.baseUrl;

  /// ワードクラウド画像を生成して取得（認証必須）
  Future<Uint8List> generateWordCloud({
    int? limit,
    int width = 800,
    int height = 400,
    String colormap = 'Reds',
  }) async {
    // クエリパラメータを構築
    final queryParams = <String, String>{
      'width': width.toString(),
      'height': height.toString(),
      'colormap': colormap,
    };

    if (limit != null) {
      queryParams['limit'] = limit.toString();
    }

    final uri = Uri.parse(
      ApiSettings.wordcloudEndpoint,
    ).replace(queryParameters: queryParams);

    final response = await http.post(
      uri,
    );

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else if (response.statusCode == 404) {
      throw Exception('会話履歴が見つかりません');
    } else {
      throw Exception('ワードクラウドの生成に失敗しました: ${response.statusCode}');
    }
  }
}
