// lib/main.dart（修正版）

import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';
import 'pages/splash_page.dart';
import 'pages/input_page.dart';
import 'pages/result_page.dart';
import 'pages/history_page.dart';
import 'pages/wc_result_page.dart';

void main() async {
  // Flutter Windowsの初期化
  WidgetsFlutterBinding.ensureInitialized();
  
  // ウィンドウマネージャー初期化（デスクトップ用）
  await windowManager.ensureInitialized();
  
  // ウィンドウ設定
  WindowOptions windowOptions = const WindowOptions(
    size: Size(1200, 800),
    minimumSize: Size(800, 600),
    center: true,
    backgroundColor: Colors.transparent,
    skipTaskbar: false,
    titleBarStyle: TitleBarStyle.normal,
    title: 'MaiChen SHITUJI',
  );
  
  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MaiChen SHITUJI',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      // スプラッシュ画面から開始
      initialRoute: '/splash',
      routes: {
        '/splash': (context) => const SplashPage(),
        '/register': (context) => const RegisterPage(),
        '/result': (context) => const ResultPage(),
        '/history': (context) => const HistoryPage(),
        '/wordcloud': (context) => const WcResultPage(),
      },
      debugShowCheckedModeBanner: false,
    );
  }
}
