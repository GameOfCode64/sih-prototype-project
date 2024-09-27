import { useEffect, useState } from "react";
import io, { Socket } from "socket.io-client";
import { Rss } from "lucide-react";
import Modal from "react-modal";

const socket: Socket = io("http://localhost:5000");

const NetworkLogs = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [logs, setLogs] = useState<any[]>([]);
  const [modalIsOpen, setIsOpen] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [currentPacket, setCurrentPacket] = useState<any>(null);

  useEffect(() => {
    socket.on("log", (data) => {
      const packetInfo = data.message;
      setLogs((prevLogs) => [...prevLogs, packetInfo]);
    });

    return () => {
      socket.off("log");
    };
  }, []);

  const openModal = (packet: unknown) => {
    setCurrentPacket(packet);
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    setCurrentPacket(null);
  };

  const formatPayload = (payload: string) => {
    return payload.replace(/\\x/g, " ").trim();
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderPacketInfo = (packet: any) => {
    return (
      <div className="bg-gray-800 text-white p-4 rounded-md shadow-md">
        <h3 className="font-bold text-lg">Packet Details</h3>
        <div className="mt-2 space-y-1">
          <div>
            <strong>Version:</strong> {packet.version}
          </div>
          <div>
            <strong>IHL:</strong> {packet.ihl}
          </div>
          <div>
            <strong>Type of Service:</strong> {packet.tos}
          </div>
          <div>
            <strong>Total Length:</strong> {packet.total_length}
          </div>
          <div>
            <strong>Identification:</strong> {packet.identification}
          </div>
          <div>
            <strong>Flags:</strong> {packet.flags}
          </div>
          <div>
            <strong>TTL:</strong> {packet.ttl}
          </div>
          <div>
            <strong>Protocol:</strong> {packet.protocol}
          </div>
          <div>
            <strong>Header Checksum:</strong> {packet.header_checksum}
          </div>
          <div>
            <strong>Source IP Address:</strong> {packet.src_ip}
          </div>
          <div>
            <strong>Destination IP Address:</strong> {packet.dst_ip}
          </div>
          <div>
            <strong>Options:</strong>{" "}
            {packet.options ? packet.options.join(", ") : "None"}
          </div>
          <div>
            <strong>Payload Data:</strong> {formatPayload(packet.payload)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="py-6 px-6 w-full">
      <p className="text-lg text-[#27bb90] font-medium flex items-center">
        <Rss className="mr-2" size={18} /> Real Time Network Logs
      </p>

      <div className="w-full mt-4 h-[80vh] bg-gray-900 text-white rounded-lg p-4 overflow-auto shadow-lg">
        <ul>
          {logs.map((log, index) => (
            <li
              key={index}
              className="my-2 flex justify-between items-center border-b border-gray-700 pb-2"
            >
              <span className="text-sm">
                {log.src_ip} ➜ {log.dst_ip} ({log.protocol})
              </span>
              <button
                className="ml-4 text-blue-500 underline hover:text-blue-300"
                onClick={() => openModal(log)}
              >
                View Details
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Modal for full packet details */}
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        className="bg-gray-900 text-white p-6 rounded-md max-w-lg mx-auto mt-20"
        overlayClassName="fixed inset-0 bg-black bg-opacity-75"
      >
        <h2 className="text-lg font-bold">Packet Details</h2>
        {currentPacket && renderPacketInfo(currentPacket)}
        <button
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={closeModal}
        >
          Close
        </button>
      </Modal>
    </div>
  );
};

export default NetworkLogs;
