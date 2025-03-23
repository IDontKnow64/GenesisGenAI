import { FC, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../../components/ui/button"
import { emailService } from "@/services/api"

const HomePage: FC = () => {
    const navigate = useNavigate();

    const onConnectEmail = () => {
        navigate("/login");
    }
    const checkEmailConnection = async () => {
        try {
          const response = await emailService.checkConnection();
          console.log(response)
          return response['connected'];
        } catch (error) {
          console.error('Connection check failed:', error);
          return false;
        }
      };
    const onNavigateMail = async () => {
        const isConnected = await checkEmailConnection();
        console.log(isConnected);
        if (isConnected) {
            navigate("/mail");
        } else {
            navigate("/login")
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
            <h1 className="text-5xl font-bold text-gray-800 mb-8 animate-fade-in">
                InboxArmour
            </h1>
            <h3 className="text-2xl text-gray-600 mb-8 animate-fade-in">
                AI-Powered Email Protection Against Scams & Phishing
            </h3>
            <div className="w-[60vw] text-center text-gray-800">
                <p>InboxArmour is a security-focused email management application that automatically scans your inbox for potential scams, phishing attempts, and suspicious content using advanced AI detection. By connecting to your email account (currently supporting Gmail), it analyzes incoming messages in real-time, flagging high-risk emails based on linguistic patterns, malicious links, and social engineering tactics.</p>
            </div>
            
            <div className="mt-8 flex flex-col items-center gap-6">
                <div className="flex flex-row items-center gap-4">
                    <Button onClick={onConnectEmail} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Manage Account
                    </Button>
                    <Button onClick={onNavigateMail} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Go to Mail
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default HomePage;