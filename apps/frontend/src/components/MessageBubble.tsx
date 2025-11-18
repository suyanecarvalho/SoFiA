interface MessageBubbleProps {
    role: "user" | "assistant";
    content: string;
}

const MessageBubble = ({ role, content }: MessageBubbleProps) => {
    const isUser = role === "user";

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
            <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    isUser
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                }`}
            >
                <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
            </div> 
        </div>
    );
};

export default MessageBubble;