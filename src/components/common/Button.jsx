export default function Button({
  text,
  backgroundColor = "white",
  border = false,
  onClick,
  icon,
  className = "",
}) {
  const bgClassMap = {
    red: "bg-[#f86b6b] text-white hover:bg-[#ef5f5f]",
    white: "bg-white text-[#202124] hover:bg-gray-100",
    transparent: "bg-transparent text-[#202124] hover:bg-gray-100",
  };

  const baseClasses =
    "inline-flex min-h-10 items-center justify-center gap-2 whitespace-nowrap rounded-md !px-5 !py-2.5 text-sm font-medium leading-none transition-colors";
  const borderClasses = border ? "border border-gray-200" : "border border-transparent";
  const colorClasses = bgClassMap[backgroundColor] ?? bgClassMap.white;

  return (
    <button type="button" onClick={onClick} className={`${baseClasses} ${borderClasses} ${colorClasses} ${className}`}>
      {icon ? <span className="text-sm">{icon}</span> : null}
      <span>{text}</span>
    </button>
  );
}
