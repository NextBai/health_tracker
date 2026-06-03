const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');
const socket = io();

let currentMetrics = {
    shoulder: '正常', head: '正常', pelvis: '正常', hunch: '正常', 
    round: '正常', spine: '正常', balance: '正常'
};

function updateMetricUI(id, status) {
    const el = document.getElementById(id);
    if(el) {
        el.textContent = status;
        el.className = status === '正常' ? 'status-good' : 'status-warn';
    }
}

function analyzePose(landmarks) {
    if (!landmarks) return;
    
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const leftEar = landmarks[7];
    const rightEar = landmarks[8];
    const leftHip = landmarks[23];
    const rightHip = landmarks[24];
    const nose = landmarks[0];

    if (leftShoulder && rightShoulder) {
        const shoulderDiff = Math.abs(leftShoulder.y - rightShoulder.y);
        currentMetrics.shoulder = shoulderDiff > 0.03 ? '高低肩' : '正常';
    }
    
    if (leftEar && leftShoulder) {
        // 簡單判斷：若耳朵在肩膀前方 (以 x 軸做近似判斷)
        const headFwd = Math.abs(leftEar.x - leftShoulder.x) > 0.05; 
        currentMetrics.head = headFwd ? '前傾' : '正常';
    }
    
    if (leftHip && rightHip) {
        const hipDiff = Math.abs(leftHip.y - rightHip.y);
        currentMetrics.pelvis = hipDiff > 0.03 ? '傾斜' : '正常';
        
        const midHipX = (leftHip.x + rightHip.x) / 2;
        const balanceDiff = Math.abs(nose.x - midHipX);
        currentMetrics.balance = balanceDiff > 0.05 ? '不平衡' : '正常';
    }
    
    // 模擬其他幾項，或者根據相同數據做出基礎推估
    currentMetrics.hunch = currentMetrics.head === '前傾' ? '駝背風險' : '正常';
    currentMetrics.round = currentMetrics.shoulder === '高低肩' ? '圓肩風險' : '正常'; 
    currentMetrics.spine = currentMetrics.pelvis === '傾斜' ? '側彎風險' : '正常';
    
    // 更新 UI
    updateMetricUI('m-shoulder', currentMetrics.shoulder);
    updateMetricUI('m-head', currentMetrics.head);
    updateMetricUI('m-pelvis', currentMetrics.pelvis);
    updateMetricUI('m-hunch', currentMetrics.hunch);
    updateMetricUI('m-round', currentMetrics.round);
    updateMetricUI('m-spine', currentMetrics.spine);
    updateMetricUI('m-balance', currentMetrics.balance);
}

function onResults(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    if(videoElement.videoWidth && canvasElement.width !== videoElement.videoWidth) {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
    }
    
    if (results.poseLandmarks) {
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                       {color: '#00ffaa', lineWidth: 4});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                      {color: '#ffffff', lineWidth: 2, radius: 3});
        
        analyzePose(results.poseLandmarks);
    }
    canvasCtx.restore();
}

const pose = new Pose({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
}});
pose.setOptions({
    modelComplexity: 0, // Lite Model for faster performance
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
pose.onResults(onResults);

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await pose.send({image: videoElement});
    },
    width: 640,
    height: 480
});
camera.start();

// 每 10 秒發送一次指標資料給後端
setInterval(() => {
    socket.emit('posture_update', currentMetrics);
}, 10000);
