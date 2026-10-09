import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update init() to check localStorage
old_init = """let GRAPH=null,crowdData={},roomData={},currentUser=USER_NODE_INIT,bestExit=null,animT=0;

async function init(){
  try{
    const r=await fetch("/api/graph");"""

new_init = """let GRAPH=null,crowdData={},roomData={},currentUser=USER_NODE_INIT,bestExit=null,animT=0;

async function init(){
  try{
    // Restoring LocalStorage State
    const savedLoc = localStorage.getItem('evac_userLoc');
    if(savedLoc) currentUser = savedLoc;
    
    const r=await fetch("/api/graph");"""

if "localStorage.getItem('evac_userLoc')" not in html:
    html = html.replace(old_init, new_init)

# 2. Update changeLocation(node) to save to localStorage
old_change = """function changeLocation(node){
  currentUser=node;
  document.getElementById("userLbl").textContent=node.replace(/_/g," ");
  calculateRoute();
}"""

new_change = """function changeLocation(node){
  currentUser=node;
  localStorage.setItem('evac_userLoc', node);
  document.getElementById("userLbl").textContent=node.replace(/_/g," ");
  calculateRoute();
}"""

if "localStorage.setItem('evac_userLoc'" not in html:
    html = html.replace(old_change, new_change)
    
# 3. Add auto-resume logic to init() for Navigation overlay
# Wait, actually just doing the above + the poll is enough, but let's check PDR mode.
# If they were walking, we can't easily resume audio context without click, so we just restore location.

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
