import { SSMClient, SendCommandCommand, GetCommandInvocationCommand } from "@aws-sdk/client-ssm";
import { EC2Client, DescribeInstanceStatusCommand } from "@aws-sdk/client-ec2";
import nodemailer from 'nodemailer';

const ssm = new SSMClient({ region: "ap-northeast-2" });
const ec2 = new EC2Client({ region: "ap-northeast-2" });

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'hayan094666@gmail.com',
        pass: 'sbfwebqzsawtymjr' // 환경 변수로 앱 비밀번호 설정
    }
});

const senderEmail = 'hayan094666@gmail.com';  // 발신 이메일 주소 (확인된 이메일 주소)
const recipientEmail = 'hayan094666@gmail.com';   // 수신 이메일 주소

const waitForCommand = async (commandId, instanceId) => {
    while (true) {
        const params = {
            CommandId: commandId,
            InstanceId: instanceId
        };
        const { Status } = await ssm.send(new GetCommandInvocationCommand(params));
        if (Status === "Success" || Status === "Failed") {
            return Status;
        }
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
};

const checkInstanceStatus = async (instanceId) => {
    const params = {
        InstanceIds: [instanceId],
    };
    const command = new DescribeInstanceStatusCommand(params);
    const response = await ec2.send(command);
    const instanceStatus = response.InstanceStatuses[0];
    return instanceStatus ? instanceStatus.InstanceState.Name : null;
};

export const handler = async (event) => {
    console.log(JSON.stringify(event));

    const instances = [
        { id: 'i-0208e8cbb3159e23e', name: 'team-hori-1-airflow-worker-2' },
        { id: 'i-0600ecc91bbd08996', name: 'team-hori-1-airflow-master' },
        { id: 'i-04a44debe7fa16f5c', name: 'team-hori-1-airflow-worker-1' }
    ];
    const logFilePath = '/home/ubuntu/s3_sync/s3_sync.log';  
    const syncCommand = 'sh /home/ubuntu/s3_sync/s3_sync.sh';
    const getLogCommand = `cat ${logFilePath}`;

    try {
        for (const instance of instances) {
            // 인스턴스 상태 확인
            const instanceStatus = await checkInstanceStatus(instance.id);
            if (instanceStatus !== "running") {
                console.log(`Instance ${instance.name} (${instance.id}) is not in a valid state: ${instanceStatus}`);
                continue;
            }

            // s3_sync.sh 스크립트 실행
            const syncParams = {
                InstanceIds: [instance.id],
                DocumentName: "AWS-RunShellScript",
                Parameters: {
                    commands: [syncCommand]
                }
            };

            const syncData = await ssm.send(new SendCommandCommand(syncParams));
            const syncCommandId = syncData.Command.CommandId;
            console.log(`Sync command sent to ${instance.name}:`, syncCommandId);

            const syncStatus = await waitForCommand(syncCommandId, instance.id);
            console.log(`Sync command status for ${instance.name}:`, syncStatus);

            if (syncStatus === "Failed") {
                throw new Error(`Sync command failed for instance ${instance.name}`);
            }

            // 로그 파일 내용 가져오기
            const logParams = {
                InstanceIds: [instance.id],
                DocumentName: "AWS-RunShellScript",
                Parameters: {
                    commands: [getLogCommand]
                }
            };

            const logData = await ssm.send(new SendCommandCommand(logParams));
            const logCommandId = logData.Command.CommandId;
            console.log(`Log command sent to ${instance.name}:`, logCommandId);

            const logStatus = await waitForCommand(logCommandId, instance.id);
            console.log(`Log command status for ${instance.name}:`, logStatus);

            if (logStatus === "Failed") {
                throw new Error(`Log command failed for instance ${instance.name}`);
            }

            const getCommandInvocationParams = {
                CommandId: logCommandId,
                InstanceId: instance.id
            };

            const commandInvocation = await ssm.send(new GetCommandInvocationCommand(getCommandInvocationParams));
            const logContent = commandInvocation.StandardOutputContent;

            const mailOptions = {
                from: senderEmail,
                to: recipientEmail,
                subject: `EC2 Log File 확인 - ${instance.name}`,
                text: logContent
            };

            await transporter.sendMail(mailOptions);
            console.log(`Email sent successfully for instance ${instance.name}`);
        }

        return {
            statusCode: 200,
            body: JSON.stringify({
                Status: "Log File Content Sent for all instances"
            }),
        };
    } catch (error) {
        console.error("Error sending command or email:", error);

        const mailOptions = {
            from: senderEmail,
            to: recipientEmail,
            subject: '에러 발생',
            text: `Error: ${error.message}`
        };

        await transporter.sendMail(mailOptions);
        console.log('Error email sent');

        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message }),
        };
    }
};
