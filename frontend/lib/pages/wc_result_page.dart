import 'package:flutter/material.dart';
import 'dart:typed_data';
import '../api/wc_service.dart';

class WcResultPage extends StatefulWidget {
  const WcResultPage({super.key});

  @override
  State<WcResultPage> createState() => _WcResultPageState();
}

class _WcResultPageState extends State<WcResultPage> {
  final WordCloudService wordcloudService = WordCloudService();
  Uint8List? imageData;
  bool isLoading = true;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadWordCloud();
  }

  Future<void> _loadWordCloud() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final data = await wordcloudService.generateWordCloud(
        width: 800,
        height: 400,
        colormap: 'Reds',
      );
      setState(() {
        imageData = data;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = e.toString();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ワードクラウド'),
        backgroundColor: Colors.blue,
      ),
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 左サイドバー（input_page.dartと同じデザイン）
          Container(
            color: Color(0xFF87CEFA),
            width: 200,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pushReplacementNamed(context, '/register');
                  },
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(150, 64),
                    alignment: Alignment.center,
                  ),
                  child: Text('入力画面', style: TextStyle(fontSize: 20)),
                ),
                SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pushReplacementNamed(context, '/history');
                  },
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(150, 64),
                    alignment: Alignment.center,
                  ),
                  child: Text('履歴表示', style: TextStyle(fontSize: 20)),
                ),
                SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () {
                    // 既にワードクラウド画面にいるのでリロード
                    _loadWordCloud();
                  },
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(150, 64),
                    alignment: Alignment.center,
                  ),
                  child: Text('ワードクラウド', style: TextStyle(fontSize: 20)),
                ),
              ],
            ),
          ),

          // メインコンテンツ
          Expanded(
            child:
                isLoading
                    ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text('ワードクラウドを生成中...'),
                        ],
                      ),
                    )
                    : errorMessage != null
                    ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.error_outline,
                            size: 64,
                            color: Colors.red,
                          ),
                          SizedBox(height: 16),
                          Text(
                            'エラー: $errorMessage',
                            style: TextStyle(color: Colors.red, fontSize: 16),
                            textAlign: TextAlign.center,
                          ),
                          SizedBox(height: 24),
                          ElevatedButton.icon(
                            onPressed: _loadWordCloud,
                            icon: Icon(Icons.refresh),
                            label: Text('再生成'),
                            style: ElevatedButton.styleFrom(
                              minimumSize: Size(150, 48),
                            ),
                          ),
                          SizedBox(height: 16),
                          TextButton(
                            onPressed: () {
                              Navigator.pushReplacementNamed(
                                context,
                                '/register',
                              );
                            },
                            child: Text('入力画面へ移動'),
                          ),
                        ],
                      ),
                    )
                    : imageData != null
                    ? Center(
                      child: SingleChildScrollView(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(height: 24),
                            Text(
                              'あなたの入力履歴のワードクラウド',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(height: 8),
                            Text(
                              '頻出する単語ほど大きく表示されます',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                            SizedBox(height: 24),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black12,
                                    blurRadius: 10,
                                    offset: Offset(0, 4),
                                  ),
                                ],
                              ),
                              padding: EdgeInsets.all(16),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.memory(
                                  imageData!,
                                  fit: BoxFit.contain,
                                ),
                              ),
                            ),
                            SizedBox(height: 24),
                            ElevatedButton.icon(
                              onPressed: _loadWordCloud,
                              icon: Icon(Icons.refresh),
                              label: Text('再生成'),
                              style: ElevatedButton.styleFrom(
                                minimumSize: Size(150, 48),
                                backgroundColor: Colors.blue,
                                foregroundColor: Colors.white,
                              ),
                            ),
                            SizedBox(height: 24),
                          ],
                        ),
                      ),
                    )
                    : const Center(child: Text('画像がありません')),
          ),
        ],
      ),
    );
  }
}
