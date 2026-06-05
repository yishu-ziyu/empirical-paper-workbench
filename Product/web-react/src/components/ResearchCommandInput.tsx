import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  ArrowUp,
  Check,
  ChevronDown,
  Copy,
  FileText,
  Loader2,
  Plus,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { cn } from "../lib/cn";

export interface FileWithPreview {
  id: string;
  file: File;
  preview?: string;
  type: string;
  uploadStatus: "pending" | "uploading" | "complete" | "error";
  uploadProgress?: number;
  textContent?: string;
}

export interface PastedContent {
  id: string;
  content: string;
  timestamp: Date;
  wordCount: number;
}

export interface ModelOption {
  id: string;
  name: string;
  description: string;
  badge?: string;
}

interface ResearchCommandInputProps {
  onSubmit?: (payload: {
    message: string;
    files: FileWithPreview[];
    pastedContent: PastedContent[];
    mode: string;
  }) => void;
  onDraftChange?: (payload: {
    message: string;
    fileCount: number;
    pastedCount: number;
    mode: string;
    hasMaterial: boolean;
  }) => void;
  disabled?: boolean;
  placeholder?: string;
  maxFiles?: number;
  maxFileSize?: number;
  modes?: ModelOption[];
}

const DEFAULT_MODES: ModelOption[] = [
  {
    id: "human-review",
    name: "半自动审阅",
    description: "每一步等待人工确认后再继续",
    badge: "默认",
  },
  {
    id: "codex-supervisor",
    name: "本地 Codex Supervisor",
    description: "先生成研究计划、风险和证据要求",
  },
  {
    id: "auto-research",
    name: "Auto Research",
    description: "自动推进到导出预检，结果保持草案层",
  },
];

const MAX_FILES = 10;
const MAX_FILE_SIZE = 50 * 1024 * 1024;
const PASTE_THRESHOLD = 200;

function makeId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}_${crypto.randomUUID()}`;
  }
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${Number.parseFloat((bytes / 1024 ** index).toFixed(1))} ${units[index]}`;
}

function getFileExtension(filename: string): string {
  const extension = filename.split(".").pop()?.toUpperCase() || "FILE";
  return extension.length > 8 ? `${extension.slice(0, 8)}...` : extension;
}

function isTextualFile(file: File): boolean {
  const extension = file.name.split(".").pop()?.toLowerCase() || "";
  const textualExtensions = new Set([
    "csv",
    "json",
    "md",
    "txt",
    "py",
    "r",
    "do",
    "sql",
    "yaml",
    "yml",
    "toml",
    "log",
    "tex",
  ]);
  return file.type.startsWith("text/") || textualExtensions.has(extension);
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => resolve((event.target?.result as string) || "");
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

function IconButton({
  children,
  label,
  disabled,
  onClick,
  className,
}: {
  children: React.ReactNode;
  label: string;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      aria-label={label}
      className={cn("icon-button", className)}
      disabled={disabled}
      title={label}
      type="button"
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function TextPreviewCard({
  label,
  title,
  content,
  onRemove,
}: {
  label: string;
  title: string;
  content: string;
  onRemove: () => void;
}) {
  return (
    <article className="preview-card text-preview-card">
      <div className="preview-card__text">{content.slice(0, 280)}</div>
      <div className="preview-card__veil">
        <span className="preview-card__type">{label}</span>
        <strong title={title}>{title}</strong>
        <div className="preview-card__actions">
          <IconButton label="复制内容" onClick={() => void navigator.clipboard.writeText(content)}>
            <Copy size={14} />
          </IconButton>
          <IconButton label="移除内容" onClick={onRemove}>
            <X size={14} />
          </IconButton>
        </div>
      </div>
    </article>
  );
}

function FilePreviewCard({ file, onRemove }: { file: FileWithPreview; onRemove: () => void }) {
  const isTextual = isTextualFile(file.file);
  if (isTextual && file.textContent) {
    return (
      <TextPreviewCard
        label={getFileExtension(file.file.name)}
        title={file.file.name}
        content={file.textContent}
        onRemove={onRemove}
      />
    );
  }

  return (
    <article className="preview-card file-preview-card">
      <FileText size={28} />
      <div className="preview-card__meta">
        <strong title={file.file.name}>{file.file.name}</strong>
        <span>{formatFileSize(file.file.size)}</span>
      </div>
      <span className="preview-card__type">{getFileExtension(file.file.name)}</span>
      <div className="preview-card__actions">
        {file.uploadStatus === "uploading" ? <Loader2 className="spin" size={15} /> : null}
        {file.uploadStatus === "error" ? <AlertCircle size={15} /> : null}
        <IconButton label="移除文件" onClick={onRemove}>
          <X size={14} />
        </IconButton>
      </div>
    </article>
  );
}

function ModeSelectorDropdown({
  modes,
  selectedMode,
  onModeChange,
}: {
  modes: ModelOption[];
  selectedMode: string;
  onModeChange: (mode: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = modes.find((mode) => mode.id === selectedMode) || modes[0];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="mode-selector" ref={ref}>
      <button
        aria-expanded={open}
        className="mode-selector__trigger"
        type="button"
        onClick={() => setOpen((value) => !value)}
      >
        <span>{selected.name}</span>
        <ChevronDown size={16} />
      </button>
      {open ? (
        <div className="mode-selector__menu" role="listbox">
          {modes.map((mode) => (
            <button
              aria-selected={mode.id === selectedMode}
              className="mode-selector__item"
              key={mode.id}
              role="option"
              type="button"
              onClick={() => {
                onModeChange(mode.id);
                setOpen(false);
              }}
            >
              <span>
                <strong>{mode.name}</strong>
                <small>{mode.description}</small>
              </span>
              {mode.badge ? <em>{mode.badge}</em> : null}
              {mode.id === selectedMode ? <Check size={16} /> : null}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function ResearchCommandInput({
  onSubmit,
  onDraftChange,
  disabled = false,
  placeholder = "输入研究题目、数据线索或下一步任务...",
  maxFiles = MAX_FILES,
  maxFileSize = MAX_FILE_SIZE,
  modes = DEFAULT_MODES,
}: ResearchCommandInputProps) {
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [pastedContent, setPastedContent] = useState<PastedContent[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedMode, setSelectedMode] = useState(modes[0]?.id || "");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = "auto";
    textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
  }, [message]);

  useEffect(() => {
    onDraftChange?.({
      message,
      fileCount: files.length,
      pastedCount: pastedContent.length,
      mode: selectedMode,
      hasMaterial: message.trim().length > 0 || files.length > 0 || pastedContent.length > 0,
    });
  }, [files.length, message, onDraftChange, pastedContent.length, selectedMode]);

  const handleFileSelect = useCallback(
    (selectedFiles: FileList | null) => {
      if (!selectedFiles || selectedFiles.length === 0) return;
      const availableSlots = Math.max(maxFiles - files.length, 0);
      const nextFiles = Array.from(selectedFiles)
        .slice(0, availableSlots)
        .filter((file) => file.size <= maxFileSize)
        .map<FileWithPreview>((file) => ({
          id: makeId("file"),
          file,
          type: file.type || "application/octet-stream",
          uploadStatus: "uploading",
          uploadProgress: 1,
        }));

      setFiles((current) => [...current, ...nextFiles]);
      nextFiles.forEach((item) => {
        if (isTextualFile(item.file)) {
          readFileAsText(item.file)
            .then((textContent) => {
              setFiles((current) =>
                current.map((file) =>
                  file.id === item.id
                    ? { ...file, textContent, uploadStatus: "complete", uploadProgress: 100 }
                    : file,
                ),
              );
            })
            .catch(() => {
              setFiles((current) =>
                current.map((file) =>
                  file.id === item.id ? { ...file, uploadStatus: "error", uploadProgress: 0 } : file,
                ),
              );
            });
        } else {
          setTimeout(() => {
            setFiles((current) =>
              current.map((file) =>
                file.id === item.id ? { ...file, uploadStatus: "complete", uploadProgress: 100 } : file,
              ),
            );
          }, 180);
        }
      });
    },
    [files.length, maxFiles, maxFileSize],
  );

  const handlePaste = useCallback(
    (event: React.ClipboardEvent<HTMLTextAreaElement>) => {
      const fileItems = Array.from(event.clipboardData.items).filter((item) => item.kind === "file");
      if (fileItems.length > 0) {
        event.preventDefault();
        const dataTransfer = new DataTransfer();
        fileItems.forEach((item) => {
          const file = item.getAsFile();
          if (file) dataTransfer.items.add(file);
        });
        handleFileSelect(dataTransfer.files);
        return;
      }

      const text = event.clipboardData.getData("text");
      if (text.length > PASTE_THRESHOLD) {
        event.preventDefault();
        setMessage((current) => `${current}${current ? "\n" : ""}${text.slice(0, PASTE_THRESHOLD)}...`);
        setPastedContent((current) => [
          ...current,
          {
            id: makeId("paste"),
            content: text,
            timestamp: new Date(),
            wordCount: text.split(/\s+/).filter(Boolean).length,
          },
        ]);
      }
    },
    [handleFileSelect],
  );

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      setIsDragging(false);
      handleFileSelect(event.dataTransfer.files);
    },
    [handleFileSelect],
  );

  const removeFile = useCallback((id: string) => {
    setFiles((current) => current.filter((file) => file.id !== id));
  }, []);

  const canSend =
    !disabled &&
    (message.trim().length > 0 || files.length > 0 || pastedContent.length > 0) &&
    files.every((file) => file.uploadStatus !== "uploading");

  function submit() {
    if (!canSend) return;
    onSubmit?.({ message, files, pastedContent, mode: selectedMode });
    setMessage("");
    setFiles([]);
    setPastedContent([]);
  }

  return (
    <section
      aria-label="研究输入器"
      className={cn("research-input", isDragging && "research-input--dragging")}
      onDragLeave={(event) => {
        event.preventDefault();
        setIsDragging(false);
      }}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDrop={handleDrop}
    >
      {isDragging ? <div className="research-input__drop">松开后添加到本次研究任务</div> : null}
      <textarea
        aria-label="输入研究题目"
        className="research-input__textarea"
        disabled={disabled}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
            event.preventDefault();
            submit();
          }
        }}
        onPaste={handlePaste}
        placeholder={placeholder}
        ref={textareaRef}
        rows={3}
        value={message}
      />
      {(files.length > 0 || pastedContent.length > 0) && (
        <div className="research-input__previews">
          {pastedContent.map((item) => (
            <TextPreviewCard
              content={item.content}
              key={item.id}
              label="PASTE"
              title={`${item.wordCount} 词 · ${item.timestamp.toLocaleTimeString("zh-CN", {
                hour: "2-digit",
                minute: "2-digit",
              })}`}
              onRemove={() => setPastedContent((current) => current.filter((entry) => entry.id !== item.id))}
            />
          ))}
          {files.map((file) => (
            <FilePreviewCard file={file} key={file.id} onRemove={() => removeFile(file.id)} />
          ))}
        </div>
      )}
      <div className="research-input__footer">
        <div className="research-input__tools">
          <IconButton
            disabled={disabled || files.length >= maxFiles}
            label="添加文件"
            onClick={() => fileInputRef.current?.click()}
          >
            <Plus size={19} />
          </IconButton>
          <IconButton disabled={disabled} label="任务参数">
            <SlidersHorizontal size={18} />
          </IconButton>
        </div>
        <div className="research-input__run">
          <ModeSelectorDropdown modes={modes} selectedMode={selectedMode} onModeChange={setSelectedMode} />
          <IconButton className="send-button" disabled={!canSend} label="开始研究" onClick={submit}>
            <ArrowUp size={20} />
          </IconButton>
        </div>
      </div>
      <input
        className="visually-hidden"
        multiple
        onChange={(event) => {
          handleFileSelect(event.target.files);
          event.currentTarget.value = "";
        }}
        ref={fileInputRef}
        type="file"
      />
    </section>
  );
}
