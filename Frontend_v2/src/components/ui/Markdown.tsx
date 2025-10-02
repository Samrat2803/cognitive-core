import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { CodeBlock } from './CodeBlock';
import './Markdown.css';

interface MarkdownProps {
  children: string;
}

export function Markdown({ children }: MarkdownProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
        // Code blocks
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';
          const code = String(children).replace(/\n$/, '');

          if (!inline && language) {
            return <CodeBlock language={language} code={code} />;
          }

          return (
            <code className="inline-code" {...props}>
              {children}
            </code>
          );
        },

        // Headings
        h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
        h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
        h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
        h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,

        // Lists
        ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
        ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
        li: ({ children }) => <li className="markdown-li">{children}</li>,

        // Blockquote
        blockquote: ({ children }) => (
          <blockquote className="markdown-blockquote">{children}</blockquote>
        ),

        // Links
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="markdown-link"
          >
            {children}
          </a>
        ),

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

        // Paragraphs
        p: ({ children }) => <p className="markdown-p">{children}</p>,

        // Strong/Bold
        strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,

        // Emphasis/Italic
        em: ({ children }) => <em className="markdown-em">{children}</em>,
      }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

