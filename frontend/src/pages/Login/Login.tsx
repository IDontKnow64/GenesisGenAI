import { FC, useState } from "react";
import { Button } from "../../components/ui/button";
import { initiateGoogleAuth } from "../../services/api";

const LoginPage: FC = () => {
  const [counter, setCounter] = useState<number>(0);

  const onConnectGmail = async () => {
    try {
      await initiateGoogleAuth();
    } catch (error) {
      // Show error to user
      alert(error);
      alert("Failed to start Google authentication");
    }
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 gap-15">
      <h1 className="text-5xl font-bold text-gray-800 mb-8 animate-fade-in">
        Connect to mail services
      </h1>
      <h2 className="text-xl text-gray-600 mb-8 animate-fade-in">
        As for now, we only support Gmail.
      </h2>

      <div className="flex flex-col items-center gap-3">
        <div className="flex flex-row items-center gap-6">
          <Button
            onClick={onConnectGmail}
            className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105"
          >
            Connect to{" "}
            <span className="inline-flex gap-0.5">
              <span style={{ color: "#4285F4" }}>G</span>
              <span style={{ color: "#EA4335" }}>o</span>
              <span style={{ color: "#FBBC05" }}>o</span>
              <span style={{ color: "#4285F4" }}>g</span>
              <span style={{ color: "#34A853" }}>l</span>
              <span style={{ color: "#EA4335" }}>e</span>
            </span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
