import 'package:flutter/material.dart';

class ResultPage extends StatefulWidget {
  const ResultPage({super.key});

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> {

  @override
  Widget build(BuildContext context) {
    final result =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;

    // データを分解
    final userInput = result?['user_input'] as String? ?? '';
    final minusWords = result?['minus_words'] as List<dynamic>? ?? [];
    final advice = result?['advice'] as String? ?? '結果がありません';

    return Scaffold(
      appBar: AppBar(
        title: const Text('AIチェック結果'),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (userInput.isNotEmpty) ...[
                Text(
                  '【あなたの入力】',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: Text(
                    userInput,
                    style: TextStyle(fontSize: 18, height: 1.5),
                  ),
                ),
                SizedBox(height: 24),
              ],

              // マイナスワードの表示
              if (minusWords.isNotEmpty) ...[
                Text(
                  '【検出されたマイナスワード】',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade700,
                  ),
                ),
                SizedBox(height: 12),
                ...minusWords.map(
                  (word) => Padding(
                    padding: const EdgeInsets.only(left: 16, bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '• ',
                          style: TextStyle(fontSize: 18, color: Colors.red),
                        ),
                        Expanded(
                          child: Text(
                            word.toString(),
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.red.shade700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                SizedBox(height: 24),
              ],

              // アドバイスの表示
              Text(
                '【AIからのアドバイス】',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Text(
                  advice,
                  style: TextStyle(fontSize: 18, height: 1.5),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
