// emailTest.mjs
import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'hayan094666@gmail.com',  // 본인의 Gmail 주소
        pass: 'sbfwebqzsawtymjr'  // 앱 비밀번호
    }
});

const senderEmail = 'hayan094666@gmail.com';  // 발신 이메일 주소 (확인된 이메일 주소)
const recipientEmail = 'hayan094666@gmail.com';  // 수신 이메일 주소

const mailOptions = {
    from: senderEmail,
    to: recipientEmail,
    subject: 'Test Email from Node.js',
    text: 'This is a test email sent from Node.js using nodemailer.'
};

transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
        return console.log(`Error: ${error}`);
    }
    console.log('Email sent: ' + info.response);
});


// 다음 명령을 사용하여 Node.js 18.x LTS 버전을 설치
//curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
//sudo apt-get install -y nodejs

//mkdir ec2-lambda-project
//cd ec2-lambda-project

// npm 초기화 및 nodemailer 설치
//npm init -y
//npm install nodemailer (이게 zip에 들어가게 될 패키지)

//node emailTest.mjs 실행했더니 메일이 성공적으로 도착

