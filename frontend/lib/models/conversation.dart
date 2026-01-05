class Conversation {
  final int id;
  final int? userId;
  final String userInput;
  // ← 削除: final String aiResponse;
  // ← 追加: 2つに分割
  final List<String> minusWords;
  final String advice;
  final DateTime createdAt;

  Conversation({
    required this.id,
    this.userId,
    required this.userInput,
    required this.minusWords, // ← 追加
    required this.advice, // ← 追加
    required this.createdAt,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'],
      userId: json['user_id'],
      userInput: json['user_input'],
      // ← 変更: 2つのフィールドに分割
      minusWords:
          json['ai_response_words'] != null
              ? List<String>.from(json['ai_response_words'])
              : [],
      advice: json['ai_response_advice'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
