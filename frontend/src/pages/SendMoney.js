import React, { useState } from "react";
import axios from "axios";

function SendMoney() {

  const [receiver, setReceiver] = useState("");

  const [amount, setAmount] = useState("");

  const sender = localStorage.getItem(
    "username"
  );

  const sendMoney = async () => {

    try {

      const response = await axios.post(
        "http://localhost:5000/send",
        {
          sender,
          receiver,
          amount
        }
      );

      alert(response.data.message);

    } catch (err) {

      alert("Transaction Failed");
    }
  };

  return (

    <div>

      <h1>Send Money</h1>

      <input
        type="text"
        placeholder="Receiver"
        onChange={(e) => setReceiver(e.target.value)}
      />

      <br /><br />

      <input
        type="number"
        placeholder="Amount"
        onChange={(e) => setAmount(e.target.value)}
      />

      <br /><br />

      <button onClick={sendMoney}>
        Send
      </button>

    </div>
  );
}

export default SendMoney;