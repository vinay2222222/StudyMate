import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { toast } from "sonner";
import { Send, User, Bot, Trash2 } from "lucide-react";

export function ChatTab({ apiBaseUrl }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem("chatHistory");
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, []);

  // Save chat history to localStorage on messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("chatHistory", JSON.stringify(messages));
    }
  }, [messages]);

  // Scroll to the latest message
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = {
      text: input,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${apiBaseUrl}/ask`, { question: input });
      const data = res.data;
      if (data.ok) {
        const chunksRes = await axios.get(`${apiBaseUrl}/chunks`);
        const chunksData = chunksRes.data;
        const botMessage = {
          text: data.answer,
          sender: "bot",
          timestamp: new Date().toLocaleTimeString(),
          references: chunksData.sample || [],
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        toast("Error", {
          description: data.error || "Failed to get answer from server",
          style: { background: "#ef4444", color: "white" },
        });
      }
    } catch (err) {
      toast("Error", {
        description:
          err.response?.data?.error ||
          "Failed to connect to the server. Check network or CORS configuration.",
        style: { background: "#ef4444", color: "white" },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem("chatHistory");
    toast("History Cleared", { description: "Chat history has been cleared." });
  };

  return (
    <Card className="shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Chat with Documents</CardTitle>
        <button
          onClick={clearHistory}
          className="p-2 text-gray-500 hover:text-red-500"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </CardHeader>
      <CardContent>
        <div
          ref={chatContainerRef}
          className="h-[500px] overflow-y-auto bg-gray-50 p-4 rounded-lg space-y-4 border border-gray-200"
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-2 ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.sender === "bot" && (
                <Bot className="h-6 w-6 text-gray-500 flex-shrink-0 mt-1" />
              )}
              <div
                className={`p-3 rounded-2xl max-w-[80%] shadow-sm ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white text-gray-800 border border-gray-200 rounded-bl-none"
                }`}
              >
                <p className="break-words text-sm">{msg.text}</p>
                <p className="text-xs mt-1 opacity-70">{msg.timestamp}</p>
                {msg.references && msg.references.length > 0 && (
                  <Accordion type="single" collapsible className="mt-2 text-xs">
                    <AccordionItem value="references">
                      <AccordionTrigger className="text-xs py-1">
                        View References
                      </AccordionTrigger>
                      <AccordionContent className="p-2 bg-gray-100 rounded-lg">
                        {msg.references.map((ref, rIdx) => (
                          <p
                            key={rIdx}
                            className="text-xs mb-1 border-l-4 border-gray-300 pl-2"
                          >
                            {ref}
                          </p>
                        ))}
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                )}
              </div>
              {msg.sender === "user" && (
                <User className="h-6 w-6 text-gray-500 flex-shrink-0 mt-1" />
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-start space-x-2 justify-start">
              <Bot className="h-6 w-6 text-gray-500 flex-shrink-0 mt-1" />
              <div className="p-3 rounded-2xl bg-white text-gray-600 border border-gray-200 rounded-bl-none shadow-sm">
                <p className="text-sm">Thinking...</p>
              </div>
            </div>
          )}
        </div>
        <div className="mt-4 flex items-center space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your question..."
            className="w-full p-3 border border-gray-300 rounded-full resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-inner"
            rows="1"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="p-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
}
