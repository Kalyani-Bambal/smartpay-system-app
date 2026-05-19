import axios from "axios";
import { useEffect, useState } from "react";

function App() {

  const [sender, setSender] = useState("");
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");

  const [transactions, setTransactions] = useState([]);

  const sendMoney = async () => {

    await axios.post("/api/send", {
      sender,
      receiver,
      amount
    });

    alert("Payment Successful");

    getTransactions();
  };

  const getTransactions = async () => {

    const response = await axios.get("/api/transactions");

    setTransactions(response.data);
  };

  useEffect(() => {
    getTransactions();
  }, []);

  return (
    <div style={{padding:"40px"}}>

      <h1>SmartPay System</h1>

      <input
        placeholder="Sender"
        onChange={(e)=>setSender(e.target.value)}
      />

      <br /><br />

      <input
        placeholder="Receiver"
        onChange={(e)=>setReceiver(e.target.value)}
      />

      <br /><br />

      <input
        placeholder="Amount"
        onChange={(e)=>setAmount(e.target.value)}
      />

      <br /><br />

      <button onClick={sendMoney}>
        Send Money
      </button>

      <hr />

      <h2>Transactions</h2>

      {
        transactions.map((txn) => (

          <div key={txn.id}>

            <p>
              <b>{txn.sender_name}</b>
              {" -> "}
              <b>{txn.receiver_name}</b>
            </p>

            <p>Amount: ₹{txn.amount}</p>

            <p>Status: {txn.status}</p>

            <p>Transaction ID: {txn.transaction_id}</p>

            <hr />

          </div>
        ))
      }

    </div>
  );
}

export default App;