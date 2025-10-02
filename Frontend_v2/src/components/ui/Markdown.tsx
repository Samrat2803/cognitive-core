import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CodeBlock } from './CodeBlock';
import './Markdown.css';

interface MarkdownProps {
  children: string;
}

export function Markdown({ children }: MarkdownProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        components={{
          // Headings
          h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
          h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
          h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
          h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,
          
          // Paragraphs
          p: ({ children }) => <p className="markdown-p">{children}</p>,
          
          // Lists
          ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
          ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
          li: ({ children }) => <li className="markdown-li">{children}</li>,
          
          // Inline elements
          strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
          em: ({ children }) => <em className="markdown-em">{children}</em>,
          code: ({ inline, children }) => 
            inline ? (
              <code className="inline-code">{children}</code>
            ) : (
              <code>{children}</code>
            ),
          
          // Links
          a: ({ href, children }) => (
            <a 
              href={href} 
              className="markdown-link" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          
          // Blockquote
          blockquote: ({ children }) => (
            <blockquote className="markdown-blockquote">{children}</blockquote>
          ),
          
          // Code blocks
          pre: ({ children }) => {
            const codeElement = React.Children.toArray(children)[0] as any;
            const language = codeElement?.props?.className?.replace('language-', '') || 'plaintext';
            const code = codeElement?.props?.children?.[0] || '';
            
            return <CodeBlock language={language} code={code} />;
          },
          
          // Tables
          table: ({ children }) => (
            <div className="markdown-table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="markdown-thead">{children}</thead>,
          tbody: ({ children }) => <tbody className="markdown-tbody">{children}</tbody>,
          tr: ({ children }) => <tr className="markdown-tr">{children}</tr>,
          th: ({ children }) => <th className="markdown-th">{children}</th>,
          td: ({ children }) => <td className="markdown-td">{children}</td>,
          
          // Horizontal rule
          hr: () => <hr className="markdown-hr" />,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

