import 'package:flutter/material.dart';
import '../api/conversation_service.dart';
import '../models/conversation.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  final ConversationService conversationService = ConversationService();
  List<Conversation> conversations = [];
  bool isLoading = true;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadConversations();
  }

  Future<void> _loadConversations() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final data = await conversationService.getConversations();
      setState(() {
        conversations = data;
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
        title: const Text('会話履歴'),
        backgroundColor: Colors.blue,
      ),
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 左サイドバー
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
                    // 既に履歴画面にいるのでリロード
                    _loadConversations();
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
                    Navigator.pushReplacementNamed(context, '/wordcloud');
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
                    ? const Center(child: CircularProgressIndicator())
                    : errorMessage != null
                    ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'エラー: $errorMessage',
                            style: TextStyle(color: Colors.red),
                          ),
                          SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: _loadConversations,
                            child: Text('再読み込み'),
                          ),
                        ],
                      ),
                    )
                    : conversations.isEmpty
                    ? const Center(
                      child: Text('履歴がありません', style: TextStyle(fontSize: 18)),
                    )
                    : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: conversations.length,
                      // ← 修正: itemBuilder（パターンA対応）
                      itemBuilder: (context, index) {
                        final conversation = conversations[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // 日時表示
                                Text(
                                  '${conversation.createdAt.year}/${conversation.createdAt.month}/${conversation.createdAt.day} ${conversation.createdAt.hour}:${conversation.createdAt.minute.toString().padLeft(2, '0')}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                  ),
                                ),
                                SizedBox(height: 8),

                                // ユーザー入力
                                Text(
                                  '【あなたの入力】',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  conversation.userInput,
                                  style: TextStyle(fontSize: 16),
                                ),
                                SizedBox(height: 12),

                                // ← 追加: マイナスワード表示
                                if (conversation.minusWords.isNotEmpty) ...[
                                  Text(
                                    '【検出されたマイナスワード】',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                      color: Colors.red.shade700,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  ...conversation.minusWords.map(
                                    (word) => Padding(
                                      padding: const EdgeInsets.only(
                                        left: 8,
                                        bottom: 4,
                                      ),
                                      child: Text(
                                        '• $word',
                                        style: TextStyle(
                                          fontSize: 16,
                                          color: Colors.red.shade700,
                                        ),
                                      ),
                                    ),
                                  ),
                                  SizedBox(height: 12),
                                ],

                                // AIアドバイス
                                Text(
                                  '【AIからのアドバイス】',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                    color: Colors.blue,
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  conversation
                                      .advice,
                                  style: TextStyle(fontSize: 16),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
          ),
        ],
      ),
    );
  }
}
