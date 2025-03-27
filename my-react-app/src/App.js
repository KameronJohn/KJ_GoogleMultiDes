import React, { useState } from "react";

const InputBox = () => {
  const [text, setText] = useState("");
  const [submittedText, setSubmittedText] = useState("");

  // Get current date and time for default values
  const currentDate = new Date().toISOString().split('T')[0]; // yyyy-mm-dd
  const currentTime = new Date().toISOString().split('T')[1].slice(0, 5); // hh:mm

  const [date, setDate] = useState(currentDate);
  const [time, setTime] = useState(currentTime);

  const arrive = "Arrive by";
  const depart = "Depart at";
  const [option, setOption] = useState(depart);

  const handleSubmit = () => {
    setSubmittedText(`URL: ${text}, Date: ${date}, Time: ${time}, Option: ${option}`);
  };
  
  // Function to clear input field
  const clearInput = () => {
    setText("");
  };

  return (
    <div className="input-box">
      <div className="input-container">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Google Map URL"
          className="input-field"
        />
        {/* Clear button */}
        {text && (
          <button onClick={clearInput} className="clear-button">
            ✖
          </button>
        )}
        <button
          onClick={handleSubmit}
          className="submit-button"
        >
          Submit
        </button>
      </div>
      <div className="select-container">
        <select
          value={depart}
          onChange={(e) => setOption(e.target.value)}
          className="select-field"
        >
          <option value={depart}>{depart}</option>
          <option value={arrive}>{arrive}</option>
        </select>
      </div>
      <div className="date-time-container">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="date-field"
        />
        <input
          type="time"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          className="time-field"
        />
      </div>

      {submittedText && (
        <p className="submitted-text">You submitted: {submittedText}</p>
      )}
    </div>
  );
};

function App() {
  return (
    <div className="app-container">
      <InputBox />
    </div>
  );
}

export default App;
