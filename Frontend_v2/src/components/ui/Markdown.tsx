import React from 'react';
import ReactMarkdown from 'react-markdown';

interface MarkdownProps {
  children: string;
}

export function Markdown({ children }: MarkdownProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  );
}

