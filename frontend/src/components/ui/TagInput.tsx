import React, { useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils'; // Assuming you have a utils file for merging classes

interface TagInputProps {
    placeholder?: string;
    tags: string[];
    setTags: (tags: string[]) => void;
    className?: string;
    maxTags?: number;
}

export const TagInput: React.FC<TagInputProps> = ({
    placeholder = "Add a tag...",
    tags,
    setTags,
    className,
    maxTags = 10
}) => {
    const [inputValue, setInputValue] = useState('');
    const [error, setError] = useState('');

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            addTag();
        } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
            removeTag(tags.length - 1);
        }
    };

    const addTag = () => {
        const trimmedInput = inputValue.trim();

        if (!trimmedInput) return;

        if (tags.length >= maxTags) {
            setError(`Max ${maxTags} tags allowed`);
            return;
        }

        if (tags.includes(trimmedInput)) {
            setError('Tag already exists');
            return;
        }

        setTags([...tags, trimmedInput]);
        setInputValue('');
        setError('');
    };

    const removeTag = (indexToRemove: number) => {
        setTags(tags.filter((_, index) => index !== indexToRemove));
        setError('');
    };

    return (
        <div className={cn("w-full", className)}>
            <div className={cn(
                "flex flex-wrap items-center gap-2 p-2 rounded-[12px] border border-[rgba(0,0,0,0.1)] bg-white focus-within:border-[#0071e3] focus-within:ring-4 focus-within:ring-[#0071e3]/10 transition-all duration-200",
                error ? "border-red-500 focus-within:ring-red-500/10" : ""
            )}>
                {tags.map((tag, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-[#0071e3]/10 text-[#0071e3] rounded-full text-sm font-medium animate-scale-in">
                        {tag}
                        <button
                            type="button"
                            onClick={() => removeTag(index)}
                            className="hover:text-[#0071e3]/70 focus:outline-none"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </span>
                ))}
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => {
                        setInputValue(e.target.value);
                        setError('');
                    }}
                    onKeyDown={handleKeyDown}
                    onBlur={addTag}
                    placeholder={tags.length === 0 ? placeholder : ''}
                    className="flex-1 min-w-[120px] bg-transparent outline-none text-sm text-[#1d1d1f] placeholder:text-[#aeaeb2] py-1 px-1"
                />
            </div>
            {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
        </div>
    );
};
