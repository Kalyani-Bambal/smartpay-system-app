import React, {
  useEffect,
  useState
} from "react";

import axios from "axios";

function Transactions() {

  const [transactions, setTransactions] =
    useState([]);

  const fetchTransactions = async () => {

    const response = await axios.get(
      "http://localhost:5000/transactions"
    );

    setTransactions(response.data);
  };

  useEffect(() => {

    fetchTransactions();

    const interval = setInterval(
      fetchTransactions,
      5000
    );

    return () => clearInterval(interval);

  }, []);

  return (

    <div>

      <h1>Transactions</h1>

      {
        transactions.map((txn) => (

          <div key={txn.id}>

            <p>
              {txn.sender}
              {" → "}
              {txn.receiver}
            </p>

            <p>
              ₹ {txn.amount}
            </p>

            <hr />

          </div>
        ))
      }

    </div>
  );
}

export default Transactions;