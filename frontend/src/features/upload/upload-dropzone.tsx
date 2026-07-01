import { FileUp, Upload } from "lucide-react";
import { type ChangeEvent, type DragEvent, useId, useState } from "react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { type UploadState } from "@/types/workspace";

const acceptedExtensions = [".txt", ".pdf", ".docx"];

type UploadDropzoneProps = {
  disabled?: boolean;
  uploadState: UploadState;
  onFileAccepted: (file: File) => void;
  onRetry?: () => void;
};

export function UploadDropzone({
  disabled = false,
  onFileAccepted,
  onRetry,
  uploadState,
}: UploadDropzoneProps) {
  const inputId = useId();
  const [isDragging, setIsDragging] = useState(false);

  const acceptFile = (file: File | undefined) => {
    if (disabled || !file || !isAcceptedFile(file.name)) {
      return;
    }
    onFileAccepted(file);
  };

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragging(false);
    acceptFile(event.dataTransfer.files[0]);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    acceptFile(event.target.files?.[0]);
    event.target.value = "";
  };

  return (
    <section
      aria-labelledby="upload-heading"
      className="flex flex-1 items-center justify-center px-4 py-10 md:px-6"
    >
      <div className="w-full max-w-2xl">
        <header className="mb-6 text-center">
          <p className="text-sm text-muted-foreground">Meeting-first workspace</p>
          <h2 id="upload-heading" className="mt-2 text-2xl font-semibold">
            Upload a meeting transcript
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Add a transcript file to open the meeting workspace with analysis tabs ready.
          </p>
        </header>
        <label
          className={cn(
            "flex min-h-72 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card px-6 py-10 text-center transition-colors hover:bg-accent/50 focus-within:ring-2 focus-within:ring-ring",
            isDragging && "bg-accent",
          )}
          htmlFor={inputId}
          onDragEnter={() => setIsDragging(true)}
          onDragLeave={() => setIsDragging(false)}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted text-muted-foreground">
            <FileUp aria-hidden="true" className="h-5 w-5" />
          </span>
          <span className="text-base font-medium">Drop txt, pdf, or docx files here</span>
          <span className="mt-2 text-sm text-muted-foreground">or browse from your computer</span>
          <Button className="mt-6" type="button" variant="secondary">
            <Upload aria-hidden="true" className="h-4 w-4" />
            Choose file
          </Button>
          <input
            accept={acceptedExtensions.join(",")}
            className="sr-only"
            disabled={disabled}
            id={inputId}
            onChange={handleFileChange}
            type="file"
          />
        </label>
        {uploadState.status !== "idle" ? (
          <div className="mt-5 rounded-lg border border-border bg-card p-4">
            <div className="mb-3 flex items-center justify-between gap-4 text-sm">
              <span className="truncate font-medium">{uploadState.fileName}</span>
              <span className="text-muted-foreground">{uploadState.progress}%</span>
            </div>
            <Progress value={uploadState.progress} />
            {uploadState.status === "error" ? (
              <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-destructive">{uploadState.error}</p>
                <Button onClick={onRetry} type="button" variant="outline">
                  Retry
                </Button>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function isAcceptedFile(fileName: string) {
  return acceptedExtensions.some((extension) => fileName.toLowerCase().endsWith(extension));
}
