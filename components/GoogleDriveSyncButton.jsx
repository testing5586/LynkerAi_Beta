// components/GoogleDriveSyncButton.jsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function GoogleDriveSyncButton({ onAuthSuccess }) {
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    // 检查 localStorage 中是否已有 access_token
    const token = localStorage.getItem("google_drive_access_token");
    const email = localStorage.getItem("google_drive_user_email");
    
    if (token && email) {
      setIsAuthorized(true);
      setUserEmail(email);
    }

    // 处理 OAuth 回调（从 URL hash 中提取 access_token）
    const hash = window.location.hash;
    if (hash.includes("access_token")) {
      const params = new URLSearchParams(hash.substring(1));
      const accessToken = params.get("access_token");
      
      if (accessToken) {
        localStorage.setItem("google_drive_access_token", accessToken);
        
        // 获取用户信息
        fetchUserInfo(accessToken);
        
        // 清除 URL hash
        window.history.replaceState(null, null, window.location.pathname);
      }
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      const data = await response.json();
      
      if (data.email) {
        localStorage.setItem("google_drive_user_email", data.email);
        setUserEmail(data.email);
        setIsAuthorized(true);
        
        if (onAuthSuccess) {
          onAuthSuccess(token, data.email);
        }
      }
    } catch (error) {
      console.error("获取用户信息失败:", error);
    }
  };

  const handleGoogleAuth = () => {
    // 从环境变量读取 Google OAuth 配置
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_GOOGLE_REDIRECT_URI || window.location.origin;
    
    if (!clientId) {
      alert("⚠️ 请先在 .env 文件中配置 VITE_GOOGLE_CLIENT_ID");
      return;
    }

    const scope = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email";
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=token&scope=${encodeURIComponent(scope)}`;

    // 在当前窗口跳转（OAuth 完成后会自动返回）
    window.location.href = authUrl;
  };

  const handleDisconnect = () => {
    localStorage.removeItem("google_drive_access_token");
    localStorage.removeItem("google_drive_user_email");
    setIsAuthorized(false);
    setUserEmail("");
  };

  return (
    <Card className="rounded-2xl shadow-md border border-gray-200 bg-white/70 backdrop-blur">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">☁️</span>
            <div>
              <h3 className="font-semibold text-gray-700">Google Drive 同步</h3>
              <p className="text-sm text-gray-500">
                {isAuthorized 
                  ? `已绑定：${userEmail}` 
                  : "仅保存 AI 记忆到个人云端"}
              </p>
            </div>
          </div>

          {isAuthorized ? (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleDisconnect}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                解除绑定
              </Button>
              <Button
                variant="default"
                size="sm"
                className="bg-green-600 hover:bg-green-700"
              >
                ✓ 已连接
              </Button>
            </div>
          ) : (
            <Button
              onClick={handleGoogleAuth}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              绑定 Google Drive
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
