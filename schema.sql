DROP TABLE IF EXISTS chat_details;

CREATE TABLE chat_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_uuid TEXT NOT NULL,
  user_input TEXT NOT NULL,
  chatbot_reply TEXT NOT NULL,
  previous_chat TEXT NOT NULL,
  openai_response TEXT NOT NULL,
  user_ip TEXT,
  user_location TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
