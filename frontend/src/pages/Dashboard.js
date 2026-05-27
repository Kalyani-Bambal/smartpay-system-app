import React from "react";

function Dashboard() {

  const username = localStorage.getItem(
    "username"
  );

  return (

    <div>

      <h1>
        Welcome {username}
      </h1>

      <a href="/send">
        Send Money
      </a>

      <br /><br />

      <a href="/transactions">
        View Transactions
      </a>

    </div>
  );
}

export default Dashboard;