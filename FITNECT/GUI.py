import streamlit as st
import subprocess



#exercises-----------------------------
def kneeraise():
    subprocess.Popen(["python", "kneeraise/fitnect-main/main.py"])
def legraise():
    subprocess.Popen(["python", "legraise/fitnect-main/main.py"])
def lunge():
    subprocess.Popen(["python", "lunge/fitnect-main/main.py"])
def pushup():
    subprocess.Popen(["python", "pushup/fitnect-main/main.py"])
def squat():
    subprocess.Popen(["python", "squats/fitnect-main/main.py"])

st.title('Fitnect')


#selection-----------------------------
exercise = None
if st.button('Knee raise'):
    exercise = kneeraise()
if st.button('leg raise'):
    exercise = legraise()
if st.button('lunge'):
    exercise = lunge()
if st.button('push up'):
    exercise = pushup()
if st.button('squat'):
    exercise = squat()

