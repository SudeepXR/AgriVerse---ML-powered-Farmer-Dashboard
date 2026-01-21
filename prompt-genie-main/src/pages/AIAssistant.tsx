import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { MessageSquare, Send, Sparkles, User, Loader2 } from 'lucide-react';

interface Message {
  id: number;
  type: 'user' | 'assistant';
  text: string;
}

const suggestedQuestions = [
  'When is the best time to sow rice?',
  'How can I improve my soil fertility?',
  'What fertilizer should I use for wheat?',
  'How to prevent pest attacks on my crops?',
];

const AIAssistant: React.FC = () => {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'assistant',
      text: 'Hello! 🌱 I am your AI farming assistant. I can help you with questions about crops, soil, weather, market prices, and more. How can I assist you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim() || isLoading) return;

    // 1. Add User Message to UI
    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      text: messageText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 2. Call the Backend API
      const response = await fetch('http://localhost:5000/api/assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from assistant');
      }

      const data = await response.json();

      // 3. Add Assistant Message to UI
      const assistantResponse: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        text: data.reply,
      };

      setMessages((prev) => [...prev, assistantResponse]);
    } catch (error) {
      // Error handling
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        text: "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.aiAssistant')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Ask any farming question and get instant, personalized advice
        </p>
      </div>

      <div className="agri-card flex flex-col h-[calc(100%-6rem)]">
        {/* Messages Container */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2"
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.type === 'assistant' && (
                <div className="w-9 h-9 rounded-xl bg-primary/15 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
              )}
              <div
                className={`max-w-[70%] p-4 rounded-2xl ${
                  message.type === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : 'bg-secondary text-foreground rounded-tl-none'
                }`}
              >
                <p className="text-sm whitespace-pre-line">{message.text}</p>
              </div>
              {message.type === 'user' && (
                <div className="w-9 h-9 rounded-xl bg-leaf/15 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-leaf" />
                </div>
              )}
            </div>
          ))}
          
          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-9 h-9 rounded-xl bg-primary/15 flex items-center justify-center flex-shrink-0">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              </div>
              <div className="bg-secondary text-muted-foreground p-4 rounded-2xl rounded-tl-none">
                <p className="text-sm italic">Thinking...</p>
              </div>
            </div>
          )}
        </div>

        {/* Suggested Questions */}
        {!isLoading && messages.length <= 2 && (
          <div className="mb-4">
            <p className="text-xs text-muted-foreground mb-2">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => handleSend(q)}
                  className="px-3 py-2 text-sm bg-secondary hover:bg-secondary/80 text-foreground rounded-full transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your farming question here..."
            className="agri-input flex-1"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="agri-btn-primary px-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;