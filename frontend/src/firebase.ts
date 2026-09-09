import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCjVWEyQ5HgzTWZSFil2-6NnrX6GSLSqaY",
  authDomain: "trustlens-d4040.firebaseapp.com",
  projectId: "trustlens-d4040",
  storageBucket: "trustlens-d4040.firebasestorage.app",
  messagingSenderId: "564043672950",
  appId: "1:564043672950:web:44ccf7cb10c5ed14c3de57",
  measurementId: "G-6SGS5P0RDD"
};

const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);
export const auth = getAuth(app);
