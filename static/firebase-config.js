// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyAZd5KZQOLkMKQUj2kQGuZqqSoFRm38z6U",
  authDomain: "equipment-system-db.firebaseapp.com",
  projectId: "equipment-system-db",
  storageBucket: "equipment-system-db.firebasestorage.app",
  messagingSenderId: "429907429862",
  appId: "1:429907429862:web:82d2ab95a7864244f3ae27",
  measurementId: "G-7BLD4GBHL5"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
