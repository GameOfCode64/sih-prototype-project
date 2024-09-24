import { Rss } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import io from "socket.io-client";

// Connect to the WebSocket server
const socket = io("http://localhost:5000");

const NetworkLogs = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    socket.on("log", (data) => {
      setLogs((prevLogs) => [...prevLogs, data.message]);
    });

    return () => {
      socket.off("log");
    };
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="flex w-full px-4 flex-col py-6 h-screen">
      <p className="text-lg text-[#27bb90] font-medium flex items-center mb-4">
        <Rss className="mr-2" size={18} /> Real Time Network Logs
      </p>

      <div
        className="w-full h-[80vh] bg-gray-900 text-white rounded-lg p-4 overflow-auto shadow-lg"
        ref={logRef}
      >
        {logs.length === 0 ? (
          <p className="text-center text-gray-400">No logs to display</p>
        ) : (
          <ul className="space-y-2">
            {logs.map((log, index) => (
              <li key={index} className="bg-gray-800 p-3 rounded-md shadow-md">
                {log}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default NetworkLogs;
