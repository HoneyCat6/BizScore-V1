import { useState, useRef, useEffect, type FormEvent } from 'react';
import { SendHorizontal, Bot, User } from 'lucide-react';
import api from '../lib/api';
import { Spinner } from '../components/Spinner';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m your BizScore assistant. I can help you understand your business score, explain financial concepts, or give tips to improve your business performance. What would you like to know?' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    const newMessages = [...messages, { role: 'user' as const, content: userMsg }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const history = newMessages.slice(1).map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const { data } = await api.post('/chat/message', {
        message: userMsg,
        conversation_history: history.slice(-10),
      });
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)]">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-500 rounded-full flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900">BizScore Assistant</h1>
            <p className="text-xs text-gray-400">Powered by AI</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
              msg.role === 'user' ? 'bg-gray-200' : 'bg-primary-500'
            }`}>
              {msg.role === 'user' ? (
                <User size={14} className="text-gray-600" />
              ) : (
                <Bot size={14} className="text-white" />
              )}
            </div>
            <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-primary-500 text-white rounded-br-md'
                : 'bg-gray-100 text-gray-800 rounded-bl-md'
            }`}>
              <p className="whitespace-pre-line">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-2.5">
            <div className="w-7 h-7 bg-primary-500 rounded-full flex items-center justify-center">
              <Bot size={14} className="text-white" />
            </div>
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
              <Spinner />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="px-5 py-3 border-t border-gray-100 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your score, tips..."
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-primary-500 text-sm"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-primary-500 text-white p-3 rounded-xl hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            <SendHorizontal size={20} />
          </button>
        </div>
      </form>
    </div>
  );
}
