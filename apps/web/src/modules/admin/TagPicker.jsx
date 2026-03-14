export function TagPicker({ options, value, onChange }) {
  const selected = new Set(value || []);
  return (
    <div className="row">
      {options.map((tag) => {
        const tagValue = tag.id ?? tag.name;
        const checked = selected.has(tagValue);
        return (
          <label key={tagValue} className="badge">
            <input
              type="checkbox"
              checked={checked}
              onChange={(event) => {
                if (event.target.checked) onChange([...(value || []), tagValue]);
                else onChange((value || []).filter((item) => item !== tagValue));
              }}
            />
            {tag.name || tagValue}
          </label>
        );
      })}
    </div>
  );
}
