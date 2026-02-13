import React from "react";

const details = [
  {
    title: "COeSi is node based tool",
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent venenatis pretium elit lacinia fermentum. Nam eget mauris a dolor sodales lacinia. Vestibulum tincidunt nunc augue, vitae pharetra sem venenatis eu. Etiam eget arcu porttitor, hendrerit risus tempor, dignissim erat. Integer molestie, nisl sit amet egestas consectetur, ligula ante fermentum libero, vitae euismod dolor justo vitae leo. Vivamus sit amet tincidunt ipsum. Duis eu enim nulla. Sed lorem magna, malesuada non vulputate et, blandit sed lorem. Praesent risus ante, dictum eget egestas convallis, hendrerit ut justo.",
    pic: "/",
  },
  {
    title: "COeSi is open source",
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent venenatis pretium elit lacinia fermentum. Nam eget mauris a dolor sodales lacinia. Vestibulum tincidunt nunc augue, vitae pharetra sem venenatis eu. Etiam eget arcu porttitor, hendrerit risus tempor, dignissim erat. Integer molestie, nisl sit amet egestas consectetur, ligula ante fermentum libero, vitae euismod dolor justo vitae leo. Vivamus sit amet tincidunt ipsum. Duis eu enim nulla. Sed lorem magna, malesuada non vulputate et, blandit sed lorem. Praesent risus ante, dictum eget egestas convallis, hendrerit ut justo.",
    pic: "/",
  },
];

const TextLeft = ({
  title,
  text,
  pic,
}: {
  title: string;
  text: string;
  pic: string;
}) => {
  return (
    <div
      style={{
        width: "100%",
        height: "500px",
        display: "flex",
        justifyContent: "space-between",
        textAlign: "left",
      }}
    >
      <div
        style={{
          width: "45%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          alignItems: "flex-start",
        }}
      >
        <h1
          style={{
            marginBottom: "50px",
            alignSelf: "flex-start",
            fontSize: "48px",
          }}
        >
          {title}
        </h1>
        <div style={{ alignSelf: "flex-start" }}>{text}</div>
      </div>
      <div
        style={{
          width: "45%",
          backgroundColor: "#FAFAFA",
          borderRadius: "20px",
        }}
      >
        <img
          src={pic}
          alt="intro pic"
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>
    </div>
  );
};

const TextRight = ({
  title,
  text,
  pic,
}: {
  title: string;
  text: string;
  pic: string;
}) => {
  return (
    <div
      style={{
        width: "100%",
        height: "500px",
        display: "flex",
        justifyContent: "space-between",
        textAlign: "left",
      }}
    >
      <div
        style={{
          width: "45%",
          backgroundColor: "#FAFAFA",
          borderRadius: "20px",
        }}
      >
        <img
          src={pic}
          alt="intro pic"
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>
      <div
        style={{
          width: "45%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          alignItems: "flex-start",
        }}
      >
        <h1
          style={{
            marginBottom: "50px",
            alignSelf: "flex-start",
            fontSize: "48px",
          }}
        >
          {title}
        </h1>
        <div style={{ alignSelf: "flex-start" }}>{text}</div>
      </div>
    </div>
  );
};

export default function DetailsSection() {
  return (
    <section
      id="details-section"
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "start",
        flexDirection: "column",
        justifyContent: "center",
        padding: "40px 80px",
        boxSizing: "border-box",
        gap: "80px",
      }}
    >
      <TextLeft
        title={details[0].title}
        text={details[0].text}
        pic={details[0].pic}
      />
      <TextRight
        title={details[1].title}
        text={details[1].text}
        pic={details[1].pic}
      />
      <TextLeft
        title={details[0].title}
        text={details[0].text}
        pic={details[0].pic}
      />
      <div style={{ width: "100%", height: "80px" }}></div>
    </section>
  );
}
