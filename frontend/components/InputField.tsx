"use client";
import React from "react";

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (val: number) => void;
}

const InputField: React.FC<InputFieldProps> = ({ label, value, onChange }) => {
  const id = label.replace(/[^a-z0-9]+/gi, '-').toLowerCase();
  return (
    <div className="flex flex-col mb-2">
      <label htmlFor={id} className="mb-1 font-medium text-sm text-gray-700 dark:text-gray-200">{label}</label>
        <input
          id={id}
          type="number"
          className="input-polished w-full"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
        />
    </div>
  );
};

export default InputField;
