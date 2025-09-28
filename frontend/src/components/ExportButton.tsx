import React, { useState } from 'react';
import { UI_CONFIG } from '../config';
import { ResearchResponse } from '../types';

interface ExportButtonProps {
  results: ResearchResponse;
  className?: string;
  disabled?: boolean;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ 
  results, 
  className = '',
  disabled = false 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const exportAsJSON = async () => {
    try {
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `research-${timestamp}.json`;
      
      const exportData = {
        exported_at: new Date().toISOString(),
        query: results.query,
        success: results.success,
        final_answer: results.final_answer,
        search_terms: results.search_terms,
        sources_count: results.sources_count,
        sources: results.sources,
        error: results.error
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      downloadBlob(blob, filename);
      return true;
    } catch (error) {
      console.error('JSON export failed:', error);
      return false;
    }
  };

  const exportAsCSV = async () => {
    try {
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `research-${timestamp}.csv`;
      
      const headers = [
        'Query',
        'Success',
        'Answer',
        'Sources Count',
        'Search Terms',
        'Sources URLs',
        'Exported At'
      ];

      const csvRow = [
        `"${escapeCSV(results.query)}"`,
        results.success.toString(),
        `"${escapeCSV(results.final_answer || '')}"`,
        results.sources_count.toString(),
        `"${results.search_terms.join(', ')}"`,
        `"${results.sources.join('; ')}"`,
        `"${new Date().toISOString()}"`
      ];

      const csvContent = [headers.join(','), csvRow.join(',')].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      downloadBlob(blob, filename);
      return true;
    } catch (error) {
      console.error('CSV export failed:', error);
      return false;
    }
  };

  const exportAsPDF = async () => {
    try {
      // Dynamic import to reduce bundle size
      const jsPDF = await import('jspdf').then(mod => mod.default);
      
      const doc = new jsPDF();
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `research-${timestamp}.pdf`;
      
      // Set up fonts and colors
      doc.setFont('helvetica');
      
      // Header
      doc.setFontSize(20);
      doc.setTextColor(40, 40, 40);
      doc.text('Research Report', 20, 30);
      
      // Query
      doc.setFontSize(14);
      doc.setTextColor(100, 100, 100);
      doc.text('Query:', 20, 50);
      doc.setFontSize(12);
      doc.setTextColor(40, 40, 40);
      
      const queryLines = doc.splitTextToSize(results.query, 170);
      doc.text(queryLines, 20, 60);
      
      let currentY = 60 + (queryLines.length * 7) + 10;
      
      // Meta information
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, currentY);
      doc.text(`Sources Found: ${results.sources_count}`, 20, currentY + 7);
      doc.text(`Search Terms: ${results.search_terms.join(', ')}`, 20, currentY + 14);
      
      currentY += 30;
      
      // Answer section
      if (results.final_answer) {
        doc.setFontSize(14);
        doc.setTextColor(40, 40, 40);
        doc.text('Answer:', 20, currentY);
        currentY += 10;
        
        doc.setFontSize(11);
        const answerLines = doc.splitTextToSize(results.final_answer, 170);
        doc.text(answerLines, 20, currentY);
        currentY += answerLines.length * 5 + 15;
      }
      
      // Sources section
      if (results.sources.length > 0) {
        doc.setFontSize(14);
        doc.setTextColor(40, 40, 40);
        doc.text('Sources:', 20, currentY);
        currentY += 10;
        
        doc.setFontSize(10);
        results.sources.slice(0, 10).forEach((source, index) => {
          if (currentY > 270) { // Start new page if needed
            doc.addPage();
            currentY = 30;
          }
          
          doc.setTextColor(40, 40, 40);
          doc.text(`${index + 1}. ${source}`, 20, currentY);
          currentY += 5;
          currentY += 3;
        });
      }
      
      doc.save(filename);
      return true;
    } catch (error) {
      console.error('PDF export failed:', error);
      return false;
    }
  };

  const handleExport = async (format: 'json' | 'csv' | 'pdf') => {
    if (disabled || isExporting) return;
    
    setIsExporting(true);
    setShowDropdown(false);
    
    try {
      let success = false;
      switch (format) {
        case 'json':
          success = await exportAsJSON();
          break;
        case 'csv':
          success = await exportAsCSV();
          break;
        case 'pdf':
          success = await exportAsPDF();
          break;
      }
      
      if (success) {
        // Could add a toast notification here
        console.log(`Successfully exported as ${format.toUpperCase()}`);
      }
    } finally {
      setIsExporting(false);
    }
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const escapeCSV = (text: string): string => {
    return text.replace(/"/g, '""');
  };

  if (!results?.success) {
    return null;
  }

  const containerStyle: React.CSSProperties = {
    position: 'relative',
    display: 'inline-block',
    fontFamily: UI_CONFIG.fonts.main
  };

  const buttonStyle: React.CSSProperties = {
    background: disabled || isExporting ? UI_CONFIG.colors.secondary : UI_CONFIG.colors.primary,
    color: disabled || isExporting ? UI_CONFIG.colors.white : UI_CONFIG.colors.darkest,
    border: 'none',
    borderRadius: '8px',
    padding: '0.75rem 1rem',
    fontWeight: 600,
    cursor: disabled || isExporting ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    transition: 'all 0.2s ease',
    minWidth: '120px',
    justifyContent: 'center'
  };

  const dropdownStyle: React.CSSProperties = {
    position: 'absolute',
    top: 'calc(100% + 0.5rem)',
    left: 0,
    right: 0,
    background: UI_CONFIG.colors.darkest,
    border: `1px solid ${UI_CONFIG.colors.primary}`,
    borderRadius: '8px',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
    zIndex: 1000,
    overflow: 'hidden'
  };

  const optionStyle: React.CSSProperties = {
    width: '100%',
    background: 'transparent',
    color: UI_CONFIG.colors.white,
    border: 'none',
    padding: '0.75rem 1rem',
    cursor: isExporting ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    transition: 'background-color 0.2s ease',
    textAlign: 'left'
  };

  return (
    <div className={className} style={containerStyle}>
      <button
        style={buttonStyle}
        onClick={() => setShowDropdown(!showDropdown)}
        disabled={disabled || isExporting}
        title="Export results"
        onMouseEnter={(e) => {
          if (!disabled && !isExporting) {
            e.currentTarget.style.background = '#a3e635';
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(217, 243, 120, 0.3)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && !isExporting) {
            e.currentTarget.style.background = UI_CONFIG.colors.primary;
            e.currentTarget.style.transform = 'none';
            e.currentTarget.style.boxShadow = 'none';
          }
        }}
      >
        <span style={{ fontSize: '1.1rem' }}>📥</span>
        <span style={{ flex: 1 }}>
          {isExporting ? 'Exporting...' : 'Export'}
        </span>
        <span style={{ fontSize: '0.8rem' }}>{showDropdown ? '▲' : '▼'}</span>
      </button>

      {showDropdown && (
        <div style={dropdownStyle}>
          <button
            style={optionStyle}
            onClick={() => handleExport('json')}
            disabled={isExporting}
            onMouseEnter={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = UI_CONFIG.colors.secondary;
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '1.1rem', width: '1.5rem', textAlign: 'center' }}>📄</span>
            <span style={{ fontWeight: 600, minWidth: '3rem' }}>JSON</span>
            <span style={{ fontSize: '0.85rem', color: UI_CONFIG.colors.secondary }}>Structured data</span>
          </button>
          
          <button
            style={{ ...optionStyle, borderTop: `1px solid ${UI_CONFIG.colors.secondary}` }}
            onClick={() => handleExport('csv')}
            disabled={isExporting}
            onMouseEnter={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = UI_CONFIG.colors.secondary;
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '1.1rem', width: '1.5rem', textAlign: 'center' }}>📊</span>
            <span style={{ fontWeight: 600, minWidth: '3rem' }}>CSV</span>
            <span style={{ fontSize: '0.85rem', color: UI_CONFIG.colors.secondary }}>Spreadsheet format</span>
          </button>
          
          <button
            style={{ ...optionStyle, borderTop: `1px solid ${UI_CONFIG.colors.secondary}` }}
            onClick={() => handleExport('pdf')}
            disabled={isExporting}
            onMouseEnter={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = UI_CONFIG.colors.secondary;
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting) {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '1.1rem', width: '1.5rem', textAlign: 'center' }}>📑</span>
            <span style={{ fontWeight: 600, minWidth: '3rem' }}>PDF</span>
            <span style={{ fontSize: '0.85rem', color: UI_CONFIG.colors.secondary }}>Formatted report</span>
          </button>
        </div>
      )}
    </div>
  );
};
