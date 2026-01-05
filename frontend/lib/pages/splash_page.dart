// lib/pages/splash_page.dart（新規）

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import '../api/api_settings.dart';

class SplashPage extends StatefulWidget {
  const SplashPage({Key? key}) : super(key: key);

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  String _statusMessage = 'AIモデルを読み込んでいます...';
  bool _hasError = false;
  int _currentRetry = 0;
  static const int _maxRetries = 30; // 30秒

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    for (int i = 0; i < _maxRetries; i++) {
      if (!mounted) return;
      
      setState(() {
        _currentRetry = i + 1;
        _statusMessage = 'バックエンドに接続中... ($_currentRetry/$_maxRetries)';
      });
      
      try {
        final response = await http
            .get(Uri.parse(ApiSettings.healthUrl))
            .timeout(const Duration(seconds: 2));
        
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          
          // モデルが読み込まれているか確認
          if (data['model_loaded'] == true) {
            if (!mounted) return;
            
            setState(() {
              _statusMessage = '✅ 準備完了';
            });
            
            // 少し待ってから遷移
            await Future.delayed(const Duration(milliseconds: 500));
            
            if (mounted) {
              Navigator.pushReplacementNamed(context, '/register');
            }
            return;
          } else {
            // サーバーは起動したがモデルはまだ読み込み中
            if (!mounted) return;
            
            setState(() {
              _statusMessage = 'モデルを読み込み中...';
            });
          }
        }
      } on TimeoutException catch (_) {
        // タイムアウト
      } catch (e) {
        // その他のエラー
        debugPrint('接続試行 ${i + 1}: $e');
      }
      
      // 1秒待機
      await Future.delayed(const Duration(seconds: 1));
    }
    
    // タイムアウト
    if (!mounted) return;
    
    setState(() {
      _hasError = true;
      _statusMessage = '❌ バックエンドの起動に失敗しました';
    });
  }

  void _retry() {
    setState(() {
      _hasError = false;
      _currentRetry = 0;
      _statusMessage = '再試行中...';
    });
    _initializeApp();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // アイコン/ロゴ
              if (!_hasError)
                const SizedBox(
                  width: 64,
                  height: 64,
                  child: CircularProgressIndicator(
                    strokeWidth: 6,
                  ),
                )
              else
                const Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Colors.red,
                ),
              
              const SizedBox(height: 32),
              
              // ステータスメッセージ
              Text(
                _statusMessage,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 16),
              
              // 進捗表示
              if (!_hasError) ...[
                Text(
                  '初回起動時は少し時間がかかります',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                // プログレスバー
                SizedBox(
                  width: 300,
                  child: LinearProgressIndicator(
                    value: _currentRetry / _maxRetries,
                  ),
                ),
              ],
              
              // エラー時の操作
              if (_hasError) ...[
                const SizedBox(height: 24),
                
                ElevatedButton.icon(
                  onPressed: _retry,
                  icon: const Icon(Icons.refresh),
                  label: const Text('再試行'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                Text(
                  'トラブルが続く場合は、以下を確認してください：\n'
                  '• アプリが正しくインストールされているか\n'
                  '• ウイルス対策ソフトがブロックしていないか\n'
                  '• ログファイルを確認（ヘルプメニュー）',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                const SizedBox(height: 16),
                
                Text(
                  'サポートが必要な場合は管理者に連絡してください',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
