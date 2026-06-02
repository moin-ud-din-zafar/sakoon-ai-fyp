import formImage from "../assets/images/form.png";

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-[#f0f5f5] flex items-center justify-center p-4">
      <div className="flex w-full max-w-[840px] rounded-2xl overflow-hidden shadow border border-gray-200 bg-primary-light">
        {/* Left — image */}
        <div className="hidden md:block w-[55%] p-4 shrink-0">
          <img
            src={formImage}
            alt="Virtual therapy session"
            className="w-full h-full object-cover rounded-xl"
          />
        </div>

        {/* Right — form slot */}
        <div className="flex-1 bg-white flex flex-col justify-center px-8 py-10 md:px-10">
          {children}
        </div>
      </div>
    </div>
  );
}
