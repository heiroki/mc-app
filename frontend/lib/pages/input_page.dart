// ========================================
// 完全版: input_page.dart
// ========================================

import 'package:flutter/material.dart';
import 'package:frontend/api/phrase_check.dart';
import 'package:frontend/api/conversation_service.dart';
import 'package:flutter/services.dart';

class RegisterPage extends StatefulWidget {
  final PhraseCheck? userService;
  final ConversationService? conversationService;

  const RegisterPage({super.key, this.userService, this.conversationService});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final textController = TextEditingController();
  late final PhraseCheck userService;
  late final ConversationService conversationService;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    userService = widget.userService ?? PhraseCheck();
    conversationService = widget.conversationService ?? ConversationService();
  }

  // ← 修正: registerPhrase()メソッド
  Future<void> registerPhrase() async {
    if (textController.text.isEmpty) {
      _showDialog('エラー', '文章を入力してください');
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final inputText = textController.text;

      // ステップ1: AI生成（Mapが返ってくる）
      final result = await userService.createPhrase(text: inputText);

      // ステップ2: DB保存（バックグラウンド処理）
      // ← 変更: minus_wordsとadviceを分けて渡す
      _saveConversationInBackground(
        inputText,
        List<String>.from(result['minus_words']),
        result['advice'] as String,
      );

      if (!mounted) return;

      final resultWithInput = {
        'user_input': inputText,
        'minus_words': result['minus_words'],
        'advice': result['advice'],
      };

      // ← 変更: Mapをそのまま渡す
      Navigator.pushNamed(context, '/result', arguments: resultWithInput);
    } catch (e) {
      if (!mounted) return;
      _showDialog('エラー', 'AI生成に失敗しました: ${e.toString()}');
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  // ← 修正: _saveConversationInBackground()メソッド
  Future<void> _saveConversationInBackground(
    String userInput,
    List<String> minusWords,
    String advice,
  ) async {
    try {
      await conversationService.saveConversation(
        userInput: userInput,
        minusWords: minusWords,
        advice: advice,
      );
      debugPrint('会話をDBに保存しました');
    } catch (e) {
      debugPrint('会話の保存に失敗: $e');
    }
  }

  void _showDialog(String title, String content, {VoidCallback? onOk}) {
    showDialog(
      context: context,
      builder:
          (_) => AlertDialog(
            title: Text(title),
            content: Text(content),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  onOk?.call();
                },
                child: const Text('OK'),
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: false,
        titleSpacing: 10,
        leadingWidth: 48,
        leading: Padding(
          padding: const EdgeInsets.only(left: 16),
          child: Image.asset(
            'assets/images/MC_main.png',
            width: 48,
            height: 48,
            fit: BoxFit.contain,
          ),
        ),
        title: const Text('入力画面', style: TextStyle(fontSize: 26)),
        backgroundColor: Colors.blue,
      ),
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            color: Color(0xFF87CEFA),
            width: 200,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () {
                    // 既に入力画面にいる場合は何もしない
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
                    Navigator.pushNamed(context, '/history');
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
                    Navigator.pushNamed(context, '/wordcloud');
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
          Expanded(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(32.0),
                  child: TextFormField(
                    controller: textController,
                    decoration: const InputDecoration(
                      labelText: '入力',
                      labelStyle: TextStyle(
                        fontSize: 28,
                        color: Colors.black,
                        fontWeight: FontWeight.bold,
                      ),
                      hintText: 'チェックしたい文を、ここに入力して下さい',
                      helperText: '※テスト用なので、一度に140文字まで入力。回答時間要(2〜3min)',
                      alignLabelWithHint: true,
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        vertical: 32.0,
                        horizontal: 16.0,
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.blue, width: 3),
                      ),
                      floatingLabelBehavior: FloatingLabelBehavior.always,
                    ),
                    keyboardType: TextInputType.multiline,
                    maxLines: 15,
                    minLines: 15,
                    inputFormatters: [LengthLimitingTextInputFormatter(140)],
                    maxLength: 140,
                    maxLengthEnforcement: MaxLengthEnforcement.enforced,
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton(
                      onPressed: isLoading ? null : registerPhrase,
                      child:
                          isLoading
                              ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                              : const Text('チェック'),
                    ),
                    const SizedBox(width: 120),
                    ElevatedButton(
                      onPressed: () {
                        textController.clear();
                      },
                      child:
                          isLoading
                              ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                              : const Text('クリア'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
