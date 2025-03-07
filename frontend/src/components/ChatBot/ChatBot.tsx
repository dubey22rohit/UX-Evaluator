import { useEffect, useRef, useState } from "react";
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

interface Message {
  type: "user" | "bot";
  content: string;
  timestamp: Date;
}

interface ChatBotProps {
  evaluationId: string;
}

const ChatBot = ({ evaluationId }: ChatBotProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      type: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/chat-analysis/${evaluationId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(`${input}`),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get response");
      }

      const data = await response.json();
      const botMessage: Message = {
        type: "bot",
        content: data.response.response || "No response available",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        type: "bot",
        content: "Sorry, I encountered an error while processing your request.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        height: "700px",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
      }}
    >
      <Typography variant="h6" gutterBottom>
        Chat with AI Assistant
      </Typography>

      <List
        sx={{
          flexGrow: 1,
          overflow: "auto",
          mb: 2,
        }}
      >
        {messages.map((message, index) => (
          <ListItem
            key={index}
            sx={{
              display: "flex",
              justifyContent:
                message.type === "user" ? "flex-end" : "flex-start",
              mb: 1,
            }}
          >
            <Box
              sx={{
                maxWidth: "70%",
                p: 1,
                borderRadius: 1,
                bgcolor: message.type === "user" ? "primary.main" : "grey.200",
                color: message.type === "user" ? "white" : "text.primary",
              }}
            >
              <Typography variant="body1">{message.content}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </Box>
          </ListItem>
        ))}
        {isLoading && (
          <ListItem
            sx={{
              display: "flex",
              justifyContent: "flex-start",
              mb: 1,
            }}
          >
            <Box
              sx={{
                display: "flex",
                gap: 0.5,
                p: 1,
                borderRadius: 1,
                bgcolor: "grey.200",
                alignItems: "center",
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  bgcolor: "text.secondary",
                  animation: "pulse 1s infinite",
                  "@keyframes pulse": {
                    "0%": {
                      opacity: 0.3,
                    },
                    "50%": {
                      opacity: 1,
                    },
                    "100%": {
                      opacity: 0.3,
                    },
                  },
                }}
              />
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  bgcolor: "text.secondary",
                  animation: "pulse 1s infinite 0.2s",
                }}
              />
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  bgcolor: "text.secondary",
                  animation: "pulse 1s infinite 0.4s",
                }}
              />
            </Box>
          </ListItem>
        )}
        <div ref={messagesEndRef} />
      </List>

      <Box
        component="form"
        noValidate
        onSubmit={handleSubmit}
        sx={{
          display: "flex",
          gap: 1,
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <Button
          type="submit"
          variant="contained"
          endIcon={<SendIcon />}
          disabled={isLoading || !input.trim()}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default ChatBot;
