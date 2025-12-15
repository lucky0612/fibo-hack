// src/components/ShotComparison.jsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, Download } from 'lucide-react';
import { getOutputUrl } from '../lib/api';

export default function ShotComparison({ shot }) {
  if (!shot.hdr_comparison_path) return null;

  const comparisonUrl = getOutputUrl(shot.hdr_comparison_path);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-cinema-dark rounded-xl border border-cinema-gray overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 bg-cinema-darker border-b border-cinema-gray flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <Eye className="w-5 h-5 text-cinema-accent" />
          HDR Comparison (8-bit vs 16-bit)
        </h3>
        
        <a
          href={comparisonUrl}
          download
          className="px-3 py-1 bg-cinema-gray hover:bg-cinema-lightgray rounded-lg text-sm flex items-center gap-2 transition-colors"
        >
          <Download className="w-4 h-4" />
          Download
        </a>
      </div>

      {/* Image */}
      <div className="p-6 bg-black">
        <img 
          src={comparisonUrl}
          alt="HDR Comparison"
          className="w-full rounded-lg"
        />
      </div>

      {/* Downloads */}
      {shot.hdr_16bit_path && (
        <div className="p-4 bg-cinema-darker border-t border-cinema-gray">
          <p className="text-sm font-semibold mb-3">Professional Exports</p>
          <div className="grid grid-cols-2 gap-3">
            <a
              href={getOutputUrl(shot.hdr_16bit_path)}
              download
              className="px-4 py-2 bg-cinema-gray hover:bg-cinema-lightgray rounded-lg text-sm text-center transition-colors"
            >
              16-bit TIFF
            </a>
            <a
              href={getOutputUrl(shot.hdr_16bit_path.replace('.tiff', '.png'))}
              download
              className="px-4 py-2 bg-cinema-gray hover:bg-cinema-lightgray rounded-lg text-sm text-center transition-colors"
            >
              16-bit PNG
            </a>
          </div>
        </div>
      )}
    </motion.div>
  );
}