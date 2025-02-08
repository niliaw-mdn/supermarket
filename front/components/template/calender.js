import React, { useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import DatePicker from "react-datepicker2";
import moment from "jalali-moment";

const Calender = () => {
  const [currentDate, setCurrentDate] = useState(moment().locale("fa"));
  const [events, setEvents] = useState([
    { id: 1, title: "جشن تولد", start: "2025-01-10", color: "red" },
    { id: 2, title: "جلسه با مشتری", start: "2025-01-15", color: "green" },
    { id: 3, title: "ناهار", start: "2025-01-20", color: "blue" },
    { id: 4, title: "جلسه ماهانه", start: "2025-01-25", color: "purple" },
  ]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: "",
    start: moment().format("jYYYY-jMM-jDD"),
    end: moment().add(1, "days").format("jYYYY-jMM-jDD"),
    color: "teal",
  });

  const handleDateClick = (info) => {
    setNewEvent({
      ...newEvent,
      start: moment(info.dateStr).locale("fa").format("jYYYY-jMM-jDD"),
    });
    setIsModalOpen(true);
  };

  const handleEventSubmit = () => {
    if (newEvent.title && newEvent.start && newEvent.end) {
      setEvents([
        ...events,
        {
          id: events.length + 1,
          title: newEvent.title,
          start: newEvent.start,
          end: newEvent.end,
          color: newEvent.color,
        },
      ]);
      setIsModalOpen(false);
    } else {
      alert("لطفاً تمامی فیلدها را پر کنید.");
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewEvent({
      ...newEvent,
      [name]: value,
    });
  };

  const renderDaysOfWeek = () => {
    const days = [
      "شنبه",
      "یک‌‌شنبه",
      "دوشنبه",
      "سه‌شنبه",
      "چهارشنبه",
      "پنج‌‌شنبه",
      "جمعه",
    ];
    return days.map((day, index) => (
      <div key={index} className="text-center text-gray-700 font-normal text-[10px] py-2">
        {day}
      </div>
    ));
  };

  const renderDaysOfMonth = () => {
    const startOfMonth = currentDate.clone().startOf("jMonth");
    const endOfMonth = currentDate.clone().endOf("jMonth");
    const startDay = startOfMonth.jDay();
    const daysInMonth = currentDate.jDaysInMonth();

    const days = [];
    for (let i = 0; i < startDay; i++) {
      days.push(<div key={`empty-${i}`} className="py-2"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      days.push(
        <div
          key={day}
          className="text-center py-2 cursor-pointer hover:bg-blue-100 rounded"
        >
          {day}
        </div>
      );
    }

    return days;
  };

  const changeMonth = (direction) => {
    setCurrentDate(
      direction === "prev"
        ? currentDate.clone().subtract(1, "jMonth")
        : currentDate.clone().add(1, "jMonth")
    );
  };

  return (
    <div className="relative w-full">
      <div
        className="border-2 mr-5 bg-white border-l-gray-500 shadow-md  shadow-black w-[320px] inline-block align-top"
        style={{ verticalAlign: "top" }}
      >
        <div className="max-w-[600px] pr-7 pt-5 mx-auto bg-white shadow rounded-lg">
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-blue-500 text-white px-4 py-2 w-[90%] rounded"
          >
            ایجاد رویداد
          </button>

          {isModalOpen && (
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
              <div className="bg-white p-8 rounded-lg shadow-lg w-96">
                <h2 className="text-xl mb-4">ایجاد رویداد جدید</h2>
                <form onSubmit={(e) => e.preventDefault()}>
                  <div className="mb-4">
                    <label className="block text-sm font-semibold">
                      نام رویداد
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={newEvent.title}
                      onChange={handleInputChange}
                      className="border w-full p-2 mt-1 rounded"
                      required
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-semibold">
                      تاریخ شروع
                    </label>
                    <DatePicker
                      name="start"
                      value={moment(newEvent.start, "jYYYY-jMM-jDD")}
                      onChange={(date) => {
                        const formattedDate = moment(date);
                        setNewEvent({
                          ...newEvent,
                          start: formattedDate
                            .locale("fa")
                            .format("jYYYY-jMM-jDD"),
                        });
                      }}
                      isGregorian={false}
                      className="border w-full p-2 mt-1 rounded"
                      required
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-semibold">
                      تاریخ پایان
                    </label>
                    <DatePicker
                      name="end"
                      value={moment(newEvent.end, "jYYYY-jMM-jDD")}
                      onChange={(date) => {
                        const formattedDate = moment(date);
                        setNewEvent({
                          ...newEvent,
                          end: formattedDate
                            .locale("fa")
                            .format("jYYYY-jMM-jDD"),
                        });
                      }}
                      isGregorian={false}
                      className="border w-full p-2 mt-1 rounded"
                      required
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-semibold">
                      رنگ رویداد
                    </label>
                    <input
                      type="color"
                      name="color"
                      value={newEvent.color}
                      onChange={handleInputChange}
                      className="w-full p-2 mt-1 rounded"
                    />
                  </div>
                  <button
                    onClick={handleEventSubmit}
                    className="bg-green-500 text-white px-4 py-2 rounded"
                  >
                    ایجاد رویداد
                  </button>
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="bg-red-500 text-white px-4 py-2 rounded ml-2"
                  >
                    بستن
                  </button>
                </form>
              </div>
            </div>
          )}
          <div className="flex justify-center flex-col">

          <div className="flex justify-between items-center py-5 w-[95%]  border-b">
            <button
              onClick={() => changeMonth("prev")}
              className="text-gray-500 hover:text-gray-700 border-2 border-slate-400 rounded-md"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8.25 4.5l7.5 7.5-7.5 7.5"
                />
              </svg>
            </button>
            <div className="text-lg font-bold text-gray-700">
              {currentDate.format("jMMMM jYYYY")}
            </div>
            <button
              onClick={() => changeMonth("next")}
              className="text-gray-500 hover:text-gray-700 border-2 border-slate-400 rounded-md"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M15.75 19.5L8.25 12l7.5-7.5"
                />
              </svg>
            </button>
          </div>
          <div className="grid grid-cols-7 gap-2 p-4">
            {renderDaysOfWeek()}
            {renderDaysOfMonth()}
          </div>
          </div>
        </div>
      </div>

      <div
        className="border-2 bg-white border-l-gray-500 shadow-md shadow-black w-[calc(100%-400px)] mr-5 inline-block align-top"
        style={{ verticalAlign: "top" }}
      >
        <div className="container mx-auto p-4 bg-white shadow-lg rounded-lg mt-8">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{
              start: "prev,next today",
              center: "title",
              end: "dayGridMonth,timeGridWeek,timeGridDay",
            }}
            events={events}
            editable={true}
            selectable={true}
            dayMaxEvents={true}
            height="auto"
            locale="fa"
            buttonText={{
              today: "امروز",
              month: "ماه",
              week: "هفته",
              day: "روز",
            }}

          />
        </div>
      </div>
    </div>
  );
};

export default Calender;
